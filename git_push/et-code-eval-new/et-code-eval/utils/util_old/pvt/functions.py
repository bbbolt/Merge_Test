
CONTEXT_CODE = """
function PivotInitialize(context, task)
{
    const pvt = context.RequirePivotTable()
    
    if (pvt || task.ID == "PVT_CREATE")    return
    
    PivotCreatePivotTable(context, "", "", "", "");
}

function get_context(task)
{
    let context = 
    {
        RequirePivotTable: function() 
        {
            if (this.pivotTable != null)
            {
                return this.pivotTable
            }
            try 
            {
                if (ActiveSheet.PivotTables(1) != null)
                    return ActiveSheet.PivotTables(1)
            }
            catch {}
            return null
        }
    }

    context.structArray = task
    
    PivotInitialize(context, task)
    return context
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

TASK2FUNC_MAP = {
    "PVT_CREATE": "PivotCreate",
    "PVT_ROWFIELD": "PivotAddRowField",
    "PVT_COLUMNFIELD": "PivotAddColumnField",
    "PVT_FILTERFIELD": "PivotAddFilterField",
    "PVT_DATETIMEFORMAT": "PivotDateFieldGroup",
    "PVT_DATASUMMARY": "PivotAddDataField",
    "PVT_FILTER": "PivotAddFilter",
    "PVT_NUMBEDIVISION": "PivotValueFieldGroup",
    "PVT_REPORTLAYOUT": "PivotReportLayout",
    "PVT_CALCULATEFIELD": "PivotAddCalculatedField",
    "PVT_PERCENT": "PivotCalculateOfPercent",
    "PVT_ADDCALITEM": "PivotAddCalculatedItemsField",
    "PVT_SUBTOTAL": "PivotSubtotal",
    "PVT_TOTALDISPLAY": "PivotTotalDisplay",
    "PVT_ADDSLICER": "PivotAddSlicer",
    "PVT_REPEATALLLABELS": "PivotRepeatAllLabels",
    "PVT_DISPLAYFIELDCAPTIONS": "PivotDisplayFieldCaptions",
    "PVT_CLEARALLFILTERS": "PivotClearAllFilters",
    "PVT_CLEARTABLE": "PivotClearTable",
    "PVT_SHOWPIVOTTABLEFIELDLIST": "PivotShowTableFieldList",
    "PVT_SHOWDRILLINDICATORS": "PivotShowDrillIndicators",
    "PVT_SELECT": "PivotSelect",
    "PVT_DELETE": "PivotDelete",
    "PVT_ADDBLANKLINE": "PivotAddBlankLine",
    "PVT_MOVEPIVOTTABLE": "PivotMove",
    "PVT_MOVEFIELD": "PivotMoveField",
    "PVT_MOVEITEM": "PivotMoveItem"
}

FUNCTIONS_MAP = {
    "PVT_CREATE": """
        PivotCreate(context, task)
    """,
    "PVT_REPEATALLLABELS":"""
        PivotRepeatAllLabels(context, task)
    """,
    "PVT_SUBTOTAL": """
        PivotSubtotal(context, task)
    """,
    "PVT_SELECT": """
        PivotSelect(context, task)
    """,
    "PVT_DISPLAYFIELDCAPTIONS": """
        PivotDisplayFieldCaptions(context, task)
    """,
    "PVT_CLEARALLFILTERS": """
        PivotClearAllFilters(context, task)
    """,
    "PVT_CLEARTABLE": """
        PivotClearTable(context, task)
    """,
    "PVT_DELETE":"""
        PivotDelete(context)
    """,
    "PVT_SHOWPIVOTTABLEFIELDLIST":"""
        PivotShowTableFieldList(context, task)
    """,
    "PVT_SHOWDRILLINDICATORS":"""
        PivotShowDrillIndicators(context, task)
    """,
    "PVT_ADDCALITEM":"""
        PivotAddCalculatedItemsField(context, task)
    """,
    "PVT_ADDSLICER":"""
        PivotAddSlicer(context, task)
    """,
    "PivotRepeatAllLabels":"""
        PivotRepeatAllLabels(context, task)
    """,
    "PVT_ADDBLANKLINE":"""
        PivotAddBlankLine(context, task)
    """,
    "PVT_TOTALDISPLAY":"""
        PivotTotalDisplay(context, task)
    """,
    "PivotSubtotal":"""
        PivotSubtotal(context, task)
    """,
    "PVT_NUMBEDIVISION":"""
        PivotValueFieldGroup(context, task)
    """,
    "PVT_PERCENT": """
        PivotCalculateOfPercent(context, task)
    """,
    "PVT_CALCULATEFIELD": """
        PivotAddCalculatedField(context, task)
    """,
    "PVT_REPORTLAYOUT":"""
        PivotReportLayout(context, task)
    """,
    "PVT_ROWFIELD": """
        PivotAddRowField(context, task)
    """,
    "PVT_COLUMNFIELD": """
        PivotAddColumnField(context, task)
    """,
    "PVT_FILTERFIELD": """
        PivotAddFilterField(context, task)
    """,
    "PVT_DATETIMEFORMAT": """
        PivotDateFieldGroup(context, task)
    """,
    "PVT_DATASUMMARY": """
        PivotAddDataField(context, task)
    """,
    "PVT_FILTER": """PivotAddFilter(context, task)""",
    "PVT_MOVEPIVOTTABLE": """PivotMove(context, task)""",
    "PVT_MOVEFIELD": """PivotMoveField(context, task)""",
    "PVT_MOVEITEM": """PivotMoveItem(context, task)"""
}

COMMON_FUNC_LST=[
    "IllegalStringParameter",
    "IllegalBooleanParameter"
]


COMMON_CODE= '''
function IllegalStringParameter(param, bEmptyStr, regex)
{
    if (undefined == param || 'string' != typeof(param))
        return true
    
    if (undefined != bEmptyStr && !bEmptyStr && "" == param)
        return true

    if (undefined != regex && !regex.test(param))
        return true

    return false
}

function IllegalBooleanParameter(param)
{
    if (undefined == param || 'boolean' != typeof(param))
        return true

    return false
}

'''

FUNCTIONS = {
    "GetXlSummaryType":'''function GetXlSummaryType(type)
{
    switch (type)
    {
        case 'Max':
            return xlMax
        case 'Min':
            return xlMin
        case 'Sum':
            return xlSum
        case 'Count':
            return xlCount
        case 'Average':
            return xlAverage
        case 'Product':
            return xlProduct
        case 'StDev':
            return xlStDev
        case 'StDevP':
            return xlStDevP
        case 'Var':
            return xlVar
        case 'VarP':
            return xlVarP
        case 'CountNums':
            return xlCountNums
        case 'Unknown':
            return xlUnknown
        default:
            return xlSum
    }
}
''',
"ContentFilter":'''function ContentFilter(field, items, bSelect)
{
    for (let i = 1; i <= field.PivotItems().Count; i++)
        field.PivotItems(i).Visible = !bSelect

    for (let i = 0; i < items.length; i++)
    {
        const name = GetEnableItemName(field, items[i])
        if (name)
            field.PivotItems(name).Visible = bSelect
    }
}''',
"ParseCellRange":'''function ParseCellRange(range)
{
    // 支出数据!$A$1:$G$2054
    let infos = {"sheetName":"","selRange":""}
    if (!range)
        return infos
    
    // 作为正常格式匹配
    let match = range.match(/^(.*?)!(.*)$/)
    if (match)
    {
        infos.sheetName = match[1]
        infos.selRange = match[2]

        return infos
    }
    
    // 只提供区域匹配
    match = range.match(/\$?[A-Z]+(\$?\d+)?(:\$?[A-Z]+(\$?\d+)?)?/)
    if (match)
    {
        infos.selRange = match[0]

        return infos
    }
    
    // 只提供工作表名称
    infos.sheetName = range

    return infos
}''',
"PivotCreatePivotTable":'''function PivotCreatePivotTable(context, ssName, sRange, dsName, dRange)
{
    try
    {
        let source      = null
        let sourceType  = xlDatabase
        let destination = null

        if (IllegalStringParameter(ssName, false))
            ssName = null
        if (IllegalStringParameter(dsName, false))
            dsName = null

        if (IllegalStringParameter(sRange, false))
            sRange = null
        if (IllegalStringParameter(dRange, false))
            dRange = null

        // 确定数据区域
        let sSheet = GetSheetByName(ssName)

        if (!ssName || !sSheet)
            sSheet = ActiveSheet

        if (sRange)
            source = sSheet.Range(sRange)
        else
        {
            let tableInfos = context.structArray

            if (undefined != tableInfos && Array.isArray(tableInfos) && tableInfos.length > 0)
                source = sSheet.Range(tableInfos[0].tableRange)
            else
                source = sSheet.UsedRange.CurrentRegion
        }

        if (0 == source.Rows.Count)
            throw new Error("数据区域为空")
        source = TrimmedHeaderRange(source)

        // 确定透视表创建区域
        let dSheet = GetSheetByName(dsName)
        let intersectRange = null
        
        if (!dSheet)
        {
            dSheet = Sheets.Add()
            if (dsName)
                dSheet.Name = dsName
        }
        
        if (!dRange)
            dRange = "A3"
        
        destination = dSheet.Range(dRange)

        intersectRange = Application.Intersect(destination, dSheet.UsedRange)
        if (intersectRange)
            destination = dSheet.UsedRange.Offset(dSheet.UsedRange.Rows.Count + 2, 0)

        const pivotCache = ActiveWorkbook.PivotCaches().Create(sourceType, source)
    
        context.pivotTable = pivotCache.CreatePivotTable(destination)
        if (destination)
            destination.Item(1, 1).Select()
    }
    catch (e)
    {
        throw new Error(e.message + "，透视表创建失败")
    }
}
''',
"IllegalStringParameter":'''function IllegalStringParameter(param, bEmptyStr, regex)
{
    if (undefined == param || 'string' != typeof(param))
        return true
    
    if (undefined != bEmptyStr && !bEmptyStr && "" == param)
        return true

    if (undefined != regex && !regex.test(param))
        return true

    return false
}''',

"PivotCreate":'''
function PivotCreate(context, task)
{
    let bNewSheet = task.bNewSheet
    let source = ParseCellRange(task.sRange)
    let destination = ParseCellRange(task.dRange)

    if (undefined == bNewSheet)
        bNewSheet = (undefined == task.dRange)

    if (bNewSheet)
        PivotCreatePivotTable(context, source.sheetName, source.selRange, "", "")
    else
        PivotCreatePivotTable(context, source.sheetName, source.selRange, destination.sheetName, destination.selRange)
}''',
"PivotGetPivotField":'''
function PivotGetPivotField(context, name)
{
    const pvt = context.RequirePivotTable()

    if (IllegalStringParameter(name, false))
        return null

    let eName = ""
    eName = GetEnableName(pvt, name)

    if (!eName)
    {
        const colStr = ExtractColumnString(name)
        if (colStr)
            eName = GetNameWithColumn(pvt, colStr)
    }

    let field = null

    if (eName)
        field = pvt.PivotFields(eName)

    return field
}''',
"PivotAddFieldToArea":'''
function PivotAddFieldToArea(context, name, orientation)
{
    let field = PivotGetPivotField(context, name)

    if (!field) return null

    if (xlDataField != orientation && field.Orientation && xlDataField != field.Orientation)
        return field

    field.Orientation = orientation
    
    return field
}''',
"PivotAddRowField":'''
function PivotAddRowField(context, task)
{
    try
    {
        if (undefined == task.name) return
        if (Array.isArray(task.name))
            for (let i = 0; i < task.name.length; i++)
                PivotAddFieldToArea(context, task.name[i], xlRowField)
        else
            PivotAddFieldToArea(context, task.name, xlRowField)
    }
    catch (e)
    {
        throw new Error(e.message + "，行字段添加失败")
    }
}''',
"PivotAddColumnField":'''
function PivotAddColumnField(context, task)
{
    try
    {
        if (undefined == task.name) return
        if (Array.isArray(task.name))
            for (let i = 0; i < task.name.length; i++)
                PivotAddFieldToArea(context, task.name[i], xlColumnField)
        else
            PivotAddFieldToArea(context, task.name, xlColumnField)
    }
    catch (e)
    {
        throw new Error(e.message + "，列字段添加失败")
    }
}''',
"PivotAddFilterField":'''
function PivotAddFilterField(context, task)
{
    let field = PivotAddFieldToArea(context, task.name, xlPageField)
    let pageItems = task.pageItems

    if (!field) return

    try
    {
        if (undefined == pageItems || !Array.isArray(pageItems))
        {
            field.CurrentPage = "(All)"
            field.EnableMultiplePageItems = false
            return
        }

        let bSelect = task.bSelect
        if (undefined == bSelect)
            bSelect = true

        // 设置多选
        field.EnableMultiplePageItems = true
        ContentFilter(field, pageItems, bSelect)
    }
    catch (e)
    {
        throw new Error(e.message + "，筛选器字段添加失败")
    }
}''',
"PivotFieldGroup":'''
function PivotFieldGroup(context, task)
{
    if (undefined == task.start)
        task.start = true
    if (undefined == task.end)
        task.end = true

    const pvt = context.RequirePivotTable()

    let field = PivotGetPivotField(context, task.name)

    if (!field) return
    if (xlRowField != field.Orientation || xlColumnField != field.Orientation)
        PivotAddRowField(context, task)

    pvt.PivotSelect(field.SourceName + "[All]", xlLabelOnly)
    Selection.Group(task.start, task.end, task.by, task.periods)
}
''',
"PivotDateFieldGroup":'''
function PivotDateFieldGroup(context, task)
{
    try
    {    
        if (undefined == task.periods || !Array.isArray(task.periods))
            task.periods = ["月"]

        let array = new Array(false, false, false, false, false, false, false)
        
        for (let i = 0; i < task.periods.length; i++)
        {
            switch (task.periods[i])
            {
                case '年': array[6] = true; break
                case '季度': array[5] = true; break
                case '月份':
                case '月': array[4] = true; break
                case '天':
                case '日': array[3] = true; break
                case '时':
                case '小时': array[2] = true; break
                case '分':
                case '分钟': array[1] = true; break
                case '秒': array[0] = true; break
                default: break
            }
        }
        task.periods = array
        PivotFieldGroup(context, task)
    }
    catch (e)
    {
        throw new Error(e.message + "，日期组合失败")
    }
}''',
"PivotValueFieldGroup":'''
function PivotValueFieldGroup(context, task)
{
    try
    {
        if (undefined == task.by)
            task.by = 1

        PivotFieldGroup(context, task)
    }
    catch (e)
    {
        throw new Error(e.message + "，数值组合失败")
    }
}''',
"PivotAddFilter":'''
function PivotAddFilter(context, task)
{
    try
    {
        let field = PivotGetPivotField(context, task.name)
        let dataField = PivotGetPivotField(context, task.dataName)
        
        if (!field) return

        // 默认添加到行字段
        if (xlRowField != field.Orientation || xlColumnField != field.Orientation)
            PivotAddRowField(context, task)
    
        if (IllegalStringParameter(task.filterType, false))
            throw new Error("filterType 参数类型错误")
    
        let type = GetXlPivotFilterType(task.filterType.toLowerCase())

        if ('string' != typeof(task.value1))
            task.value1 = "" + task.value1
        if ('string' != typeof(task.value2))
            task.value2 = "" + task.value2

        // 修正操作符不对应问题
        if (IsDateTypeValue(task.value1))
        {
            if (type == xlCaptionIsBetween)
                type = xlDateBetween
            else if (type == xlCaptionIsNotBetween)
                type = xlDateNotBetween
        }
        field.PivotFilters.Add(type, dataField, task.value1, task.value2)
    }
    catch (e)
    {
        throw new Error(e.message + "，字段添加筛选失败")
    }
}
''',
"PivotContentFilter":'''
function PivotContentFilter(context, task)
{
    try
    {
        let field = PivotGetPivotField(context, task.name)
        
        if (!field) return

        // 默认添加到行字段
        if (xlRowField != field.Orientation || xlColumnField != field.Orientation)
            PivotAddRowField(context, task)

        let pageItems = task.pageItems
        let bSelect = task.bSelect

        if (undefined == pageItems || !Array.isArray(pageItems))
            return

        if (undefined == bSelect)
            bSelect = true

        ContentFilter(field, pageItems, bSelect)
    }
    catch (e)
    {
        throw new Error(e.message + "，内容筛选设置失败")
    }
}''',
"PivotMoveField":'''
function PivotMoveField(context, task)
{
    try
    {
        const pvt = context.RequirePivotTable()
        let field = PivotGetPivotField(context, task.name)
        
        if (!field) return

        let pos = field.Position
        let rows = pvt.RowFields().Count
        let cols = pvt.ColumnFields().Count
        let dir = task.dir
        let orientation = field.Orientation

        if (undefined == dir)   return
        if (xlRowField != orientation && xlColumnField != orientation)  return

        dir = dir.toLowerCase()
        switch (dir)
        {
            case 'start':
            case 'leftmost':
                pos = 1; break;
            case 'end':
            case 'rightmost':
                pos = (xlRowField == orientation) ? rows : cols; break;
            case 'left':
            case 'up':
                pos = (pos == 1) ? 1 : pos - 1;
                break;
            case 'right':
            case 'down':
                pos = (xlRowField == orientation) ? (pos == rows ? rows : pos + 1) : (pos == cols ? cols : pos + 1);
                break;
            case 'movetorow':
                if (xlColumnField == orientation) 
                {
                    orientation = xlRowField; pos = rows + 1;
                }
                break;
            case 'movetocol':
                if (xlRowField == orientation)
                {
                    orientation = xlColumnField; pos = cols + 1;
                }
                break;
        }

        field.Position = pos
        field.Orientation = orientation
    }
    catch(e)
    {
        throw new Error(e.message + "，字段移动失败")
    }
}
''',
"PivotMoveItem":'''
function PivotMoveItem(context, task)
{
    try
    {
        let field = PivotGetPivotField(context, task.name)
        
        if (!field) return

        let itemName = GetEnableItemName(field, task.iName)

        if (!itemName)  return

        let item = field.PivotItems(itemName)
        let pos = item.Position
        let count = field.PivotItems().Count
        let dir = task.dir

        if (undefined == dir)   return

        dir = dir.toLowerCase()
        switch (dir)
        {
            case 'start':
            case 'leftmost':
                pos = 1; break;
            case 'end':
            case 'rightmost':
                pos = count; break;
            case 'left':
            case 'up':
                pos = (pos == 1) ? 1 : pos - 1;
                break;
            case 'right':
            case 'down':
                pos = (pos == count) ? count : pos + 1;
                break;
        }

        item.Position = pos
    }
    catch(e)
    {
        throw new Error(e.message + "，数据项移动失败")
    }
}''',
"PivotMove":'''
function PivotMove(context, task)
{
    try
    {
        let bNewSheet = task.bNewSheet
        let dRange = ParseCellRange(task.dRange)
        let pvt = context.RequirePivotTable()

        if (undefined == bNewSheet)
            bNewSheet = (undefined == task.dRange)

        if (!dRange.sheetName)
            dRange.sheetName = ActiveSheet.Name

        if (bNewSheet)
            pvt.Location = ""
        else
            pvt.Location = dRange.sheetName + "!" + dRange.selRange
    }
    catch (e)
    {
        throw new Error(e.message + "，移动透视表失败")
    }
}''',
"PivotDeleteField":'''
function PivotDeleteField(context, task)
{
    try
    {
        let field = PivotGetPivotField(context, task.name)

        if (field)
            field.Orientation = xlHidden
    }
    catch (e)
    {
        throw new Error(e.message + "，删除字段失败")
    }
}
''',
"PivotAddDataField":'''function PivotAddDataField(context, task)
{
    try
    {
        let summary = GetXlSummaryType(task.summary)
        let field = PivotAddFieldToArea(context, task.name, xlDataField)
    
        // 汇总计数时可以使用任意字段，此时对错误字段进行一次修正
        if (xlCount == summary && !field)
        {
            let pvt = context.RequirePivotTable()
        
            if (pvt.PivotFields().Count > 0)
            {
                field = pvt.PivotFields(0)
                if (field)  field.Orientation = xlDataField
            }
        }
        if (!field) return null
        field.Function = summary

        return field
    }
    catch (e)
    {
        return null
    }
}
''',
"PivotCalculateOfPercent":'''
function PivotCalculateOfPercent(context, task)
{
    try
    {
        let field = PivotAddDataField(context, task)

        if (!field) return

        let parentField = PivotGetPivotField(context, task.parentName)
        let currentField = PivotGetPivotField(context, task.curName)

        field.Calculation = xlNormal;
        field.NumberFormat = "General";

        if (parentField && currentField && !IsDateTypeValue(task.parentName) && !IsDateTypeValue(task.curName))
        {
            if (xlRowField == parentField.Orientation && xlRowField == currentField.Orientation)
            {
                // 父行汇总百分比
                field.Calculation = xlPercentOfParentRow
                field.NumberFormat = "0.00%"
            }
            else if (xlColumnField == parentField.Orientation && xlColumnField == currentField.Orientation)
            {
                // 父列汇总百分比
                field.Calculation = xlPercentOfParentColumn
                field.NumberFormat = "0.00%"
            }
            else if (xlRowField == parentField.Orientation && xlColumnField == currentField.Orientation)
            {
                // 行汇总百分比
                field.Calculation = xlPercentOfRow
                field.NumberFormat = "0.00%"
            }
            else if (xlColumnField == parentField.Orientation && xlRowField == currentField.Orientation)
            {
                // 列汇总百分比
                field.Calculation = xlPercentOfColumn
                field.NumberFormat = "0.00%"
            }
        }
        else
        {
            // 总计百分比
            field.Calculation = xlPercentOfTotal
            field.NumberFormat = "0.00%"
        }
    }
    catch (e)
    {
        throw new Error(e.message + "，百分比显示方式设置失败")
    }
}''',
"PivotAddCalculatedField":'''
function PivotAddCalculatedField(context, task)
{
    try
    {
        const pvt = context.RequirePivotTable()

        let cf = pvt.CalculatedFields()

        // 未提供计算字段名称，默认"字段N"
        if (undefined == task.calName)
        {
            let max = 0
            for (let i = 1; i <= cf.Count; i++)
            {
                let name = cf.Item(i).Name
                let regex = /^字段[1-9]\d*$/
                if (regex.test(name))
                {
                    let num = parseInt(name.substring(2))
                    if (num > max)
                        max = num
                }
            }
            task.calName = "字段" + (max + 1)
        }

        if (undefined == task.formula)
            task.formula = "=0"

        cf.Add(task.calName, task.formula)
        pvt.PivotFields(task.calName).Orientation = xlDataField
    }
    catch (e)
    {
        throw new Error(e.message + "，计算字段添加失败")
    }
}
''',
"PivotAddCalculatedItemsField":'''
function PivotAddCalculatedItemsField(context, task)
{
    try
    {
        const pvt = context.RequirePivotTable()
        let field = PivotGetPivotField(context, task.name)

        if (!field)
            throw new Error("字段 " + task.name + " 不存在")

        let citems = field.CalculatedItems()

        // 未提供计算项名称，默认"公式N"
        if (IllegalStringParameter(task.itemName, false))
        {
            let max = 0
            for (let i = 1; i <= citems.Count; i++)
            {
                let name = citems.Item(i).Name
                let regex = /^公式[1-9]\d*$/
                if (regex.test(name))
                {
                    let num = parseInt(name.substring(2))
                    if (num > max)
                        max = num
                }
            }
            task.itemName = "公式" + (max + 1)
        }

        if (IllegalStringParameter(task.formula, false, /^=/))
            task.formula = "=0"

        pvt.PivotSelect(field.SourceName + "[All]", xlLabelOnly)
        citems.Add(task.itemName, task.formula)
    }
    catch (e)
    {
        throw new Error(e.message + "，计算项添加失败")
    }
}''',
"PivotSubtotal":'''
function PivotSubtotal(context, task)
{
    try
    {
        const pvt = context.RequirePivotTable()

        if ("Bottom" == task.location)
        {
            pvt.SubtotalLocation(xlAtBottom)
        }
        else if ("Top" == task.location)
        {
            pvt.SubtotalLocation(xlAtTop)
        }
    }
    catch (e)
    {
        throw new Error(e.message + "，分类汇总设置失败")
    }
}''',
"PivotTotalDisplay":'''function PivotTotalDisplay(context, task)
{
    try
    {
        const pvt = context.RequirePivotTable()
        let display = task.display
        let bColGrand = false
        let bRowGrand = false

        if (!Array.isArray(display))   return

        for (let i = 0; i < display.length; i++)
        {
            let field = PivotGetPivotField(context, display[i])

            if (!field) return

            if (xlRowField == field.Orientation)
                bRowGrand = true
            else if (xlColumnField == field.Orientation)
                bColGrand = true
        }

        pvt.ColumnGrand = bColGrand
        pvt.RowGrand = bRowGrand
    }
    catch (e)
    {
        throw new Error(e.message + "，行列启用/禁用设置失败")
    }
}
''',
"PivotReportLayout":'''function PivotReportLayout(context, task)
{
    try
    {
        const pvt = context.RequirePivotTable()
        let layout = GetXlLayoutRowType(task.layout)

        pvt.RowAxisLayout(layout)
    }
    catch (e)
    {
        throw new Error(e.message + "，报表布局设置失败")
    }
}
''',
"GetSheetByName":'''function GetSheetByName(name)
{
    try
    {
        if (IllegalStringParameter(name, false))
            return null

        let sheet = null

        for (let i = 1; i <= Sheets.Count; i++)
        {
            if (Sheets.Item(i).Name == name)
            {
                sheet = Sheets.Item(i)
                break
            }
        }

        return sheet
    }
    catch (e)
    {
        return null
    }
}''',
"TrimmedHeaderRange":'''function TrimmedHeaderRange(range)
{
    let cols = range.Columns.Count
    let rows = range.Rows.Count
    let lcell = range.Cells(1, 1)
    let rcell = range.Cells(1, cols)
    let lcol = range.Column
    let rcol = lcol + cols - 1

    if (!lcell.Value2)
        lcol = lcell.End(xlToRight).Column
    if (!rcell.Value2)
        rcol = rcell.End(xlToLeft).Column

    return range.Offset(0, lcol - range.Column).Resize(rows, rcol - lcol + 1)
}''',
"GetEnableName": '''function GetEnableName(pvt, name)
{
    let sources = []
    let count = GetCountOfPivotField(pvt)

    for (let i = 1; i <= count; i++)
        sources.push(pvt.PivotFields(i).Name)

    count = pvt.DataFields().Count
    for (let i = 1; i <= count; i++)
        sources.push(pvt.DataFields(i).Name)

    return GetBestMatchString(sources, name)
}''',
"IsDateTypeValue":'''function IsDateTypeValue(value)
{
    if (IllegalStringParameter(value))  return false

    let regex = ""

    // YYYY-MM-DD
    regex = /^\d{4}-\d{1,2}-\d{1,2}$/
    if (regex.test(value)) return true

    // YYYY/MM/DD
    regex = /^\d{4}\/\d{1,2}\/\d{1,2}$/
    if (regex.test(value)) return true

    return false
}''',
"GetBestMatchString":'''function GetBestMatchString(sources, match)
{
    if (undefined == sources || !Array.isArray(sources) || IllegalStringParameter(match, false))
        return null

    let max = 0
    let res = ""

    for (let i = 0; i < sources.length; i++)
    {
        let source = sources[i];
        let suit = CalculateSimilarity(match, source)
        if (suit > max)
        {
            max = suit
            res = source
        }
    }

    return res
}''',
"GetCountOfPivotField":'''function GetCountOfPivotField(pvt)
{
    try
    {
        let count = pvt.PivotFields().Count

        if (pvt.DataFields().Count > 1)
            count--

        return count
    }
    catch (e)
    {
        return 0
    }
}''',
"GetNameWithColumn":'''function GetNameWithColumn(pvt, col)
{
    try
    {
        let cacheIndex = pvt.CacheIndex
        let cache = ActiveWorkbook.PivotCaches().Item(cacheIndex)
        // =月考成绩!R2C1:R22C8
        let sourceData = cache.SourceData
        let name = ""
    
        const regex = /^=(.*?)!R(\d+)C(\d+):R(\d+)C(\d+)$/
        const matches = sourceData.match(regex)
        if (matches)
        {
            const sheetName = matches[1].replace(/^'|'$/g, '')
            const startRow = parseInt(matches[2])
            const startColumn = parseInt(matches[3])
            const endRow = parseInt(matches[4])
            const endColumn = parseInt(matches[5])
      
            let wss = ActiveWorkbook.Worksheets
            let sourceSheet = wss.Item(sheetName)
            let startPoint = sourceSheet.Cells.Item(startRow, startColumn)
            let endPoint = sourceSheet.Cells.Item(endRow, endColumn)
            let sourceRange = sourceSheet.Range(startPoint, endPoint)
            let columnRange = getRange(sourceRange, col)
      
            name = columnRange.Cells.Item(1, 1).Value2
        }
        
        return name
    }
    catch (e)
    {
        return ""
    }
}''',
"CalculateSimilarity":'''function CalculateSimilarity(str1, str2)
{
    const len1 = str1.length
    const len2 = str2.length
    
    const dp = []
    for (let i = 0; i <= len1; i++)
    {
        dp[i] = []
        dp[i][0] = i
    }
    for (let j = 0; j <= len2; j++)
    {
        dp[0][j] = j
    }
    
    for (let i = 1; i <= len1; i++)
    {
        for (let j = 1; j <= len2; j++)
        {
            if (str1[i - 1] === str2[j - 1])
            {
                dp[i][j] = dp[i - 1][j - 1]
            }
            else
            {
                dp[i][j] = Math.min(
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + 1
                )
            }
        }
    }
    
    return 1 - dp[len1][len2] / Math.max(len1, len2)
}''',
"ExtractColumnString":'''function ExtractColumnString(str)
{
    const colStr = str.match(/[a-zA-Z]+/g)
    if (colStr)
        return colStr[0]

    return null
}''',
"PivotAddSlicer":'''function PivotAddSlicer(context, task)
{
    try
    {
        const pvt = context.RequirePivotTable()
        let field = PivotGetPivotField(context, task.name)

        if (!field) return
        
        let fieldName = field.Name
        let cache = AddSlicerToPivotTable(pvt, fieldName)
        let select = task.select
        let bSelect = task.bSelect

        // 默认全选
        if (undefined == select || !Array.isArray(select))
            return

        // 默认正向选择
        if (undefined == bSelect)
            bSelect = true

        for (let i = 1; i <= cache.SlicerItems.Count; i++)
            cache.SlicerItems(i).Selected = !bSelect

        for (let i = 0; i < select.length; i++)
        {
            const name = GetEnableItemName(field, select[i])
            if (name)
                cache.SlicerItems(name).Selected = bSelect
        }
    }
    catch (e)
    {
        throw new Error(e.message + "，切片器插入失败")
    }
}''',
"AddSlicerToPivotTable":'''function AddSlicerToPivotTable(pvt, fieldName)
{
    let cache = null
    let caches = ActiveWorkbook.SlicerCaches

    try
    {
        cache = caches.Add2(pvt, fieldName)
        AddSlicerToCache(cache, fieldName)
        return cache
    }
    catch (e)
    {
        for (let i = 1; i <= caches.Count; i++)
        {
            cache = caches.Item(i)
            if (cache.SourceName != fieldName)
                continue
            for (let j = 1; j <= cache.PivotTables.Count; j++)
            {
                let pvtTmp = cache.PivotTables.Item(j)
                if (pvt.Name == pvtTmp.Name)
                {
                    AddSlicerToCache(cache, fieldName)
                    return cache
                }
            }
        }
        throw new Error("字段 " + task.name + " 不存在")
    }
    return null
}
''',
"AddSlicerToCache": '''function AddSlicerToCache(cache, fieldName)
{
    let slicerName = fieldName
    let sameIndex = 1
        
    while (sameIndex < 100)
    {
        try
        {
            cache.Slicers.Add(ActiveSheet, null, slicerName, fieldName, 187.5, 92.25, 144, 176.25)
            return
        }
        catch (e)
        {
            slicerName = fieldName + " " + sameIndex
            sameIndex++
        }
    }

    throw new Error("添加相同名称切片器超过" + sameIndex + "个")
}
''',
"PivotRepeatAllLabels": '''function PivotRepeatAllLabels(context, task)
{
    try
    {
        const pvt = context.RequirePivotTable()

        if (IlleagalBooleanParameter(task.bRepeatLabels))
            throw new Error("参数未定义或参数类型错误")

        let repeat = xlDoNotRepeatLabels
        
        if (task.bRepeatLabels)
            repeat = xlRepeatLabels

        pvt.PivotFields(1).RepeatAllLabels(repeat)
    }
    catch (e)
    {
        throw new Error(e.message + "，重复项目标签设置失败")
    }
}''',
"PivotShowTableFieldList": '''function PivotShowTableFieldList(context, task)
{
    try
    {
        if (IlleagalBooleanParameter(task.bShowList))
            throw new Error("参数未定义或参数类型错误")

        ActiveWorkbook.ShowPivotTableFieldList = task.bShowList
    }
    catch (e)
    {
        throw new Error(e.message + "，显示字段列表设置失败")
    }
}''',
"PivotShowDrillIndicators":'''function PivotShowDrillIndicators(context, task)
{
    try
    {
        const pvt = context.RequirePivotTable()

        if (IlleagalBooleanParameter(task.bShowDrillIndicator))
            throw new Error("参数未定义或参数类型错误")

        pvt.ShowDrillIndicators = task.bShowDrillIndicator
    }
    catch (e)
    {
        throw new Error(e.message + "，+/- 按钮设置失败")
    }
}''',
"PivotDisplayFieldCaptions": '''function PivotDisplayFieldCaptions(context, task)
{
    try
    {
        const pvt = context.RequirePivotTable()
        
        if (IlleagalBooleanParameter(task.bDisplayFieldCaptions))
            throw new Error("参数未定义或参数类型错误")

        pvt.DisplayFieldCaptions = task.bDisplayFieldCaptions
    }
    catch (e)
    {
        throw new Error(e.message + "，显示字段设置失败")
    }
}''',
"PivotClearAllFilters": '''function PivotClearAllFilters(context, task)
{
    try
    {
        let pvt = context.RequirePivotTable()

        pvt.ClearAllFilters()    
    }
    catch (e)
    {
        throw new Error(e.message + "，清理筛选失败")
    }
}''',
"PivotClearTable": '''function PivotClearTable(context, task)
{
    try
    {
        let pvt = context.RequirePivotTable()

        pvt.ClearTable()
    }
    catch (e)
    {
        throw new Error(e.message + "，透视表清理失败")
    }
}''',
"PivotSelect": '''function PivotSelect(context, task)
{
    try
    {
        let pvt = context.RequirePivotTable()
        let mode = GetXlPTSelectionModeType(task.mode)
        
        pvt.PivotSelect("", mode)
    }
    catch(e)
    {
        throw new Error(e.message + "，透视表选择失败")
    }
}''',
"PivotDelete": '''function PivotDelete(context)
{
    try
    {
        let pvt = context.RequirePivotTable()

        pvt.PivotSelect("", xlDataAndLabel)
        Selection.Clear()
    }
    catch (e)
    {
        throw new Error(e.message + "，透视表删除失败")
    }
}''',
"GetXlPTSelectionModeType": '''function GetXlPTSelectionModeType(type)
{
    switch (type)
    {
        case 'xlBlanks':
            return xlBlanks
        case 'xlButton':
            return xlButton
        case 'xlDataAndLabel':
            return xlDataAndLabel
        case 'xlDataOnly':
            return xlDataOnly
        case 'xlFirstRow':
            return xlFirstRow
        case 'xlLabelOnly':
            return xlLabelOnly
        case 'xlOrigin':
            return xlOrigin
        default:
            return xlDataAndLabel
    }
}''',
"GetXlLayoutRowType":'''function GetXlLayoutRowType(type)
{
    switch (type)
    {
        case 'xlCompactRow':
            return xlCompactRow
        case 'xlOutlineRow':
            return xlOutlineRow
        case 'xlTabularRow':
            return xlTabularRow
        default:
            return xlOutlineRow
    }
}''',
"GetXlPivotFilterType": '''function GetXlPivotFilterType(type)
{    
    switch (type)
    {
        case 'greaterthan':
        case '>':
            return xlCaptionIsGreaterThan
        case 'greaterthanorequal':
        case '>=':
            return xlCaptionIsGreaterThanOrEqualTo
        case 'lessthan':
        case '<':
            return xlCaptionIsLessThan
        case 'lessthanorequal':
        case '<=':
            return xlCaptionIsLessThanOrEqualTo
        case 'equal':
        case '=':
            return xlCaptionEquals
        case 'notblank':
        case 'notequal':
        case '<>': 
        case '!=':
            return xlCaptionDoesNotEqual
        case 'between':
            return xlCaptionIsBetween
        case 'notbetween':
            return xlCaptionIsNotBetween
        case 'datebetween':
            return xlDateBetween
        case 'datenotbetween':
            return xlDateNotBetween
        default:
            return xlCaptionEquals
    }
}''',
"PivotAddBlankLine": '''function PivotAddBlankLine(context, task)
{
    try
    {
        const pvt = context.RequirePivotTable()

        if (IlleagalBooleanParameter(task.bBlankLine))
            throw new Error("参数未定义或参数类型错误")

        let count = GetCountOfPivotField(pvt)

        for (let i = 1; i <= count; i++)
        {
            pvt.PivotFields(i).LayoutBlankLine = task.bBlankLine
        }
    }
    catch (e)
    {
        throw new Error(e.message + "，空白行添加失败")
    }
}
''',
"IllegalBooleanParameter":'''function IlleagalBooleanParameter(param)
{
    if (undefined == param || 'boolean' != typeof(param))
        return true

    return false
}''',
"GetEnableItemName": '''function GetEnableItemName(field, name)
{
    try
    {
        let items = field.PivotItems()
        let sources = []
        let match = ""
    
        for (let i = 1; i <= items.Count; i++)
            sources.push(items.Item(i).Name)
        match = GetBestMatchString(sources, name)

        return match
    }
    catch(e)
    {
        return ""
    }
}'''
}