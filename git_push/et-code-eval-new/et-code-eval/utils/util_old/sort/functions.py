CONTEXT_CODE = """
function GetActiveRange()
{
    // 尝试获取CurrentRegion，若工作表被保护则返回UsedRange
    let rng = ActiveSheet.UsedRange
    try
    {
        rng = rng.CurrentRegion
    }
    catch(e) {}
    return rng
}

function get_context(task)
{
    let context = 
    {
        RequireSort: function()
        {
            if (this.sort == null)
                this.sort = {}
            return this.sort
        }
    }

    let targetWorksheet = ActiveSheet
    let targetWorkbook = ActiveWorkbook
    let currentRange = GetActiveRange()
    let targetRange;
    if (task.column)
        targetRange = currentRange.Columns(task.column)
    else if (task.range)
        targetRange = Range(task.range)
    
    return [task, targetWorksheet, currentRange, context]
}


"""

TASK_CODE = """
    let task = <<<PARA_DEF_CODE>>>
    
"""


MARCO_FUNC = """

function Macro()
{
<<<TASK_CODE_AND_FUNC_CODE>>>
}

"""


FUNCTIONS_MAP = {
    "SORT_CUSTOMLIST": """
    SortCreateCustomList(context, task)
    """,
    "SORT_ONVALUE": """
    SortAddSortField(context, task, xlSortOnValues, currentRange)
    """,
    "SORT_ONCOLOR": """
    SortOnColor(context, task, xlSortOnCellColor, currentRange)
    """,
    "SORT_ONICON": """
    SortAddSortField(context, task, xlSortOnIcon, currentRange)
    """,
    "SORT_ONRANDOM": """
    SortOnRandom(context, task, xlSortOnValues, currentRange)
    """,
    "SORT_APPLY": """
    SortApply(context, task, targetWorksheet)
    """
}

FUNCTIONS = {
"SortApply": """function SortApply(context, task, targetWorksheet)
{
    if (!task.range) return
    let sortRange;
    let bHasHead = true;

    if(context.structArray != null){
        let tableInfo = GetTableStructsOfRange(context.structArray, task.range);
        // 1.用户指定的排序区域为整个表单->包含表头bHasHead=true
        // 2.用户指定排序表单部分区域内容->不包含表头bHasHead=false
        if(tableInfo[0].headRange != null && Application.Intersect(Range(task.range), Range(tableInfo[0].headRange)) == null)
            bHasHead = false;
        // 实际处理区域为用户指定区域与表单区域的交集
        if(tableInfo.length > 0  && tableInfo[0].tableRange != null)
            sortRange = Application.Intersect(Range(task.range), Range(tableInfo[0].tableRange));
    }
    else{
        sortRange = Range(task.range)
    }
    
    let matchCase = false
    if (task.match_case != null)
        matchCase = !!task.match_case

    let sort = context.RequireSort()

    var  realSort = targetWorksheet.Sort

    realSort.SortFields.Clear()
    realSort.SetRange(sortRange)

    if (bHasHead)
        realSort.Header = xlYes
    else
        realSort.Header = xlNo

    realSort.MatchCase = matchCase
    realSort.Orientation = xlTopToBottom

    for (let item of sort.fields) {
        realSort.SortMethod = item.method
        switch (item.sortOn) {
            case xlSortOnValues:
                realSort.SortFields.Add(item.key, item.sortOn, item.order, item.custom)
                break
            case xlSortOnCellColor:
            if(item.colorindex == null){
                    realSort.SortFields.Add(item.key, item.sortOn, item.order).SortOnValue.Color = item.color
                }
                else{
                    realSort.SortFields.Add(item.key, item.sortOn, item.order).SortOnValue.ColorIndex = item.colorindex
                }
                break
            case xlSortOnFontColor:
                realSort.SortFields.Add(item.key, item.sortOn, item.order).SortOnValue.Color = item.color
                break
            case xlSortOnIcon:
                realSort.SortFields.Add(item.key, item.sortOn, item.order).SetIcon(item.icon)
            default:
                break
        }

    }
    realSort.Apply()
}""",
"SortOnRandom": """function SortOnRandom(context, task, xlSortOnValues, currentRange)
{
    // 打乱texts序列顺序作为CustomList
    let texts = GetRangeTexts(task.key, context)
    texts = RandomArray(texts)

    let list = texts.join(',')
    let sort = context.RequireSort()
    if (!sort.customlist)
        sort.customlist = {}
    sort.customlist["随机排序"] = list
    task.custom = "随机排序";
    // 以自定义序列xlSortOnValues进行SortAddSortField
    SortAddSortField(context, task, xlSortOnValues, currentRange)
}
""",
"GetRangeTexts": """function GetRangeTexts(key, context) 
{
    let tableRange = GetTableRangeFromKey(context, key);
    const dataRange = tableRange.Rows(`2:${tableRange.Rows.Count}`);
    let range = getRange(dataRange, key);

    if (range != null) 
    {
        // Set存储不重复的内容
        let uniqueContents = new Set();
        for (let i = 1; i <= range.Rows.Count; i++) 
        {
            let content = range.Cells.Item(i, 1).Value2;
            uniqueContents.add(content);
        }

        let uniqueArray = Array.from(uniqueContents);
        return uniqueArray;
    }
    return [];
}""",
"RandomArray": """function RandomArray(array) 
{
    // 将array中的随机打乱顺序返回
    let currentIndex = array.length;

    while (currentIndex !== 0) 
    {
        // 获取0-Index之间的随机一项
        let randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex -= 1;

        let temp = array[currentIndex];
        array[currentIndex] = array[randomIndex];
        array[randomIndex] = temp;
    }
    return array;
}""",

"SortOnColor": """function SortOnColor(context, task, xlSortOnCellColor, currentRange)
{
    // 当为全颜色排序时
    if(task.color == "all")
    {
        // 获取key列的全部相关颜色，遍历添加颜色排序方案
        const colors = GetKeyColors(task.key, task.type, context)
        for (var i = 0; i < colors.length; i++)
        {
            task.color = colors[i]
            SortAddSortField(context, task, xlSortOnCellColor, currentRange)
        }
    }
    // 否则执行正常排序方案
    else
    {
        SortAddSortField(context, task, xlSortOnCellColor, currentRange)
    }
}
""",
"GetKeyColors" : """function GetKeyColors(key, type, context) 
{
    let tableRange = GetTableRangeFromKey(context, key);
    const dataRange = tableRange.Rows(`2:${tableRange.Rows.Count}`);
    let range = getRange(dataRange, key)

    if (range != null) 
    {
        // Set存储不重复的color
        let colors = new Set();
        for (let i = 1; i <= range.Rows.Count; i++) 
        {
            let cell = range.Cells(i, 1);
            let color;

            if (type == 'cell')
                color = cell.Interior.Color;
            else if (type == 'font')
                color = cell.Font.Color;

            colors.add(color);
        }

        // 将Set转化为数组并映射每一元素成为RGB值
        let uniqueColors = Array.from(colors).map(color => [
            color & 0xff,
            (color & 0xff00) >> 8,
            (color & 0xff0000) >> 16
        ]);

        return uniqueColors;
    }
    return [];
}

""",

"SortAddSortField": """function SortAddSortField(context, task, sortOn, currentRange)
{
    if (!task.key) return

    let order = xlAscending
    if (typeof(task.order) == 'string') {
        switch (task.order.toLowerCase()) {
            case 'descending':
            case 'desc': order = xlDescending; break
            default: order = xlAscending; break
        }
    }
    if (sortOn == xlSortOnCellColor) {
        if (typeof(task.type) == 'string') {
            switch (task.type.toLowerCase()) {
                case 'cell': sortOn = xlSortOnCellColor; break
                case 'font': sortOn = xlSortOnFontColor; break
                default: break
            }
        }
    }

    let method = xlPinYin
    if (task.method != null) {
        if (typeof(task.method) == 'string') {
            if (task.method.toLowerCase() == 'stroke') {
                method = xlStroke
            }
        }
    }

    // TODO: 横向排序
    let tableRange = GetTableRangeFromKey(context, task.key);
    const dataRange = tableRange.Rows(`2:${tableRange.Rows.Count}`)
    let key = getRange(dataRange, task.key)

    let sort = context.RequireSort()
    if (!sort.fields) {
        sort.fields = []
    }
    let field = {key:key, order:order, sortOn: sortOn, method:method}
    switch (sortOn) {
        case xlSortOnValues:
            if (task.custom != null)
                field.custom = sort.customlist[task.custom]
            break
        case xlSortOnCellColor:
        case xlSortOnFontColor:
            if (task.color != null) {
                if(task.color == 'none' || task.color == 'null'){
                    field.colorindex = xlNone
                }else if (Array.isArray(task.color)){
                    let color = CheckColorIsInRange(sortOn, task.color, key)
                    field.color = RGB(...color)
                }
            }else
                field.colorindex = xlNone
            break
        case xlSortOnIcon:
            field.icon = GetSortIcon(key, task)
        default:
            break
    }
    sort.fields.push(field)
}""",

"getRange": """function getRange(crg, col)
{
    return Application.Intersect(crg.Rows.EntireRow, Columns(col))
}
""",
"CheckColorIsInRange": """function CheckColorIsInRange(sorton, color, range){
    let minDistance = null;
    let similarColor = null;
    let userHSV = rgb2hsv([color[0], color[1], color[2]]);

    var colorsArray = new Array();
    for(let i = 1;i <= range.Rows.Count; i++){
        let curColor = null;
        if(sorton == xlSortOnCellColor){
            curColor = range.Rows(i).Interior.Color
        }
        else{
            curColor = range.Rows(i).Font.Color
        }
        let  red = curColor & 0x000000FF
        let  green = (curColor & 0x0000FF00) >> 8
        let  blue = (curColor & 0x00FF0000) >> 16
        if(red == color[0] && green == color[1] && blue == color[2])
            return color;
        if(colorsArray.indexOf(curColor) != -1)
             continue;
        colorsArray.push(curColor);

        let curHSV = rgb2hsv([red, green, blue])
        let dis = DistanceOf(userHSV, curHSV)
      
        if(minDistance == null || dis < minDistance){
            minDistance = dis;
            similarColor = [red, green, blue];
        }
    }

    return similarColor
}""",
"rgb2hsv": """function rgb2hsv(arr) {
    let h = 0, s = 0, v = 0;
    let r = arr[0], g = arr[1], b = arr[2];
    arr.sort(function (a, b) {
        return a - b;
    });
    let max = arr[2];
    let min = arr[0];
    v = max / 255;
    if (max === 0) {
        s = 0;
    } else {
        s = 1 - (min / max);
    }
    if (max === min) {
        h = 0; // 事实上，max===min的时候，h无论为多少都无所谓
    } else if (max === r && g >= b) {
        h = 60 * ((g - b) / (max - min)) + 0;
    } else if (max === r && g < b) {
        h = 60 * ((g - b) / (max - min)) + 360;
    } else if (max === g) {
        h = 60 * ((b - r) / (max - min)) + 120;
    } else if (max === b) {
        h = 60 * ((r - g) / (max - min)) + 240;
    }
    h = parseInt(h);
    s = parseInt(s * 100);
    v = parseInt(v * 100);
    return {"H":h, "S":s, "V":v};
}""",
"DistanceOf": """function DistanceOf(hsv1, hsv2){
    const R = 100;
    const angle = 30;
    let h = R * Math.cos(angle / 180 * Math.PI);
    let r = R * Math.sin(angle / 180 * Math.PI);

    let x1 = r * hsv1.V * hsv1.S * Math.cos(hsv1.H / 180 * Math.PI);
    let y1 = r * hsv1.V * hsv1.S * Math.sin(hsv1.H / 180 * Math.PI);
    let z1 = h * (1 - hsv1.V);
    let x2 = r * hsv2.V * hsv2.S * Math.cos(hsv2.H / 180 * Math.PI);
    let y2 = r * hsv2.V * hsv2.S * Math.sin(hsv2.H / 180 * Math.PI);
    let z2 = h * (1 - hsv2.V);
    let dx = x1 - x2;
    let dy = y1 - y2;
    let dz = z1 - z2;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
}""",
"GetSortIcon": """function GetSortIcon(sortRg, task){

    if(sortRg.FormatConditions.Count == 0)
       return null
    let iconsetID = sortRg.FormatConditions.Item(1).IconSet.ID
    if(iconsetID <= 0 || iconsetID > 20)
       return null
    if(task.icon_shape == null || typeof(task.icon_shape) != 'string')
      return null
    switch(task.icon_shape.toLowerCase()){
        case 'arrow' : return GetIDByArrow(iconsetID, task);
        case 'circle': return GetIDByTrafficLight(iconsetID, task);
        default: break;
        //triangle, star其它形状对应的枚举待补充
    }
    return null
}""",
"GetIDByArrow": """function GetIDByArrow(iconSetID, task){
    if(task.direction == null || typeof(task.direction) != 'string')
        return null
    
    let  itemId = -1
    switch(task.direction.toLowerCase()){
        case 'down':{
            itemId =1;
            break;
        }
        case 'Slop_down':{
            if(IsArrow4(iconSetID) ||  IsArrow5(iconSetID))
                itemId = 2;
            break;
        }
        case 'transverse':{
            if(IsArrow3(iconSetID))
                itemId = 2;
            if(IsArrow5(iconSetID))
                itemId = 3;
            break;
        }
        case 'slope_up':{
            if(IsArrow4(iconSetID))
                itemId = 3;
            if(IsArrow5(iconSetID))
                itemId = 4;
            break;
        }
        case 'up':{
            if(IsArrow3(iconSetID))
                itemId = 3;
            if(IsArrow4(iconSetID))
                itemId = 4;
            if(IsArrow5(iconSetID))
                itemId = 5;
            break;
        }
    }
    if(itemId == -1)
        return null;
    return ActiveWorkbook.IconSets(iconSetID).Item(itemId)
}""",
"IsArrow3":"""function  IsArrow3(iconSetID){
    if(iconSetID == xl3Arrows || iconSetID == xl3ArrowsGray)
      return true;
    return false;
}""",

"IsArrow4": """function  IsArrow4(iconSetID){
    if(iconSetID == xl4Arrows || iconSetID == xl4ArrowsGray)
      return true;
    return false;
}
""",
"IsArrow5": """function  IsArrow5(iconSetID){
    if(iconSetID == xl5Arrows || iconSetID == xl5ArrowsGray)
      return true;
    return false;
}""",
"GetIDByTrafficLight": """function GetIDByTrafficLight(iconSetID, task){
    if(task.icon_color == null || typeof(task.icon_color) != 'string')
        return null
    let isTrafficlLights = false
    if(iconSetID == xl3Triangles || iconSetID == xl3TrafficLights1 || iconSetID == xl3TrafficLights2 || iconSetID == xl3Signs || iconSetID == xl4TrafficLights)
        isTrafficlLights = true;
    if(isTrafficlLights == false)
        return null
    let  itemId = -1
    switch(task.icon_color.toLowerCase()){
        case 'green': itemId = 1; break;
        case 'yellow': itemId = 2; break;
        case 'red': itemId = 3; break;
        case 'black':{
            if(iconSetID == xl4TrafficLights)
                itemId = 4;
            break;
        } 
    }
    if(itemId == -1)
      return null;
    return ActiveWorkbook.IconSets(iconSetID).Item(itemId)   
}""",



"SortCreateCustomList":"""function SortCreateCustomList(context, task)
{
    if (!task.list && !task.key || !task.name) return

    if (Array.isArray(task.list)) 
    {
        task.list = FindCustomList(task.list)
        task.list = task.list.join(',')
    }
    // 有依据排序的列时按照key所指列内容为CustomList
    if (task.key && Array.isArray(GetRangeTexts(task.key, context)))
        task.list = GetRangeTexts(task.key, context).join(',')
    
    let sort = context.RequireSort()
    if (!sort.customlist)
        sort.customlist = {}
    sort.customlist[task.name] = task.list
}       
    """,
"GetRangeTexts": """function GetRangeTexts(key, context) 
{
    let tableRange = GetTableRangeFromKey(context, key);
    const dataRange = tableRange.Rows(`2:${tableRange.Rows.Count}`);
    let range = getRange(dataRange, key);

    if (range != null) 
    {
        // Set存储不重复的内容
        let uniqueContents = new Set();
        for (let i = 1; i <= range.Rows.Count; i++) 
        {
            let content = range.Cells.Item(i, 1).Value2;
            uniqueContents.add(content);
        }

        let uniqueArray = Array.from(uniqueContents);
        return uniqueArray;
    }
    return [];

}
""",
"GetTableRangeFromKey": """function GetTableRangeFromKey(context, key)
{
    let tableRange = null;
    if(context.structArray != null)
    {
        let tableInfo = GetTableStructsOfRange(context.structArray, key + ":" + key);
        if(tableInfo.length > 0  && tableInfo[0].tableRange != null)
            tableRange = Range(tableInfo[0].tableRange);
    }
    // 表结构识别区域获取错误
    if(tableRange == null)
        tableRange = ActiveSheet.UsedRange;
    return tableRange;
}

""",
"GetTableStructsOfRange": """function GetTableStructsOfRange(tableInfos, range)
{
    let intersectTables = []

    if (undefined == tableInfos || undefined == range
        || !Array.isArray(tableInfos) || tableInfos.length <= 0 || 'string' != typeof(range))
        return intersectTables

    for (let i = 0; i < tableInfos.length; i++)
    {
        let range1 = ActiveSheet.Range(tableInfos[i].tableRange)
        let range2 = ActiveSheet.Range(range)
        let intersectRange = Application.Intersect(range1, range2)

        if (intersectRange)
            intersectTables.push(tableInfos[i])
    }

    if (0 == intersectTables.length)
        intersectTables.push(tableInfos[0])

    return intersectTables
}
""",

"FindCustomList": """function FindCustomList(list)
{
    const  customList = [['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],['Sun','Mon','Tue','Wed','Thu','Fri','Sat'],
     ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],['January','February','March','April','May','June','July','August','September','October','November','December'],
     ['日','一','二','三','四','五','六'],['星期日','星期一','星期二','星期三','星期四','星期五','星期六'],['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月'],
     ['第一季','第二季','第三季','第四季'],['第一季度','第二季度','第三季度','第四季度'],['正月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','腊月'],
     ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥'],['甲','乙','丙','丁','戊','己','庚','辛','壬','癸'],
     ['小学','初中','高中','专科','本科','研究生','博士'] ];

     if(list == null)
        return list;
    let curList = null
    const  str = list[0]
    for (let arrItem of customList){
      for(let item of arrItem){
          if(item == str){
            curList = arrItem
            break;
           }
      }
    }

    if(curList != null){
        if(list.length == curList.length && list[0] == curList[0]) //长度一样，第一个一样，则
            return list
        if(list[0] == curList[0]) //长度不一样的情况，都是从头开始
            return curList
        let index = curList.indexOf(str);
        if(index <= 0)
            return list
        let frontArr = curList.slice(0, index)
        let backArr = curList.slice(index, curList.length)
        return backArr.concat(frontArr)
    }    

    return list
}
""",
"GetActiveRange":"""function GetActiveRange()
{
    // 尝试获取CurrentRegion，若工作表被保护则返回UsedRange
    let rng = ActiveSheet.UsedRange
    try
    {
        rng = rng.CurrentRegion
    }
    catch(e) {}
    if (!rng)
        rng = ActiveSheet.UsedRange
    return rng
}""",
"get_context":"""function get_context(task)
{
    let context = 
    {
        RequireSort: function()
        {
            if (this.sort == null)
                this.sort = {}
            return this.sort
        }
    }

    let targetWorksheet = ActiveSheet
    let targetWorkbook = ActiveWorkbook
    let currentRange = GetActiveRange()
    let targetRange;
    if (task.column)
        targetRange = currentRange.Columns(task.column)
    else if (task.range)
        targetRange = Range(task.range)

    return [task, targetWorksheet, currentRange, context]
}"""

}