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
    if (!rng)
        rng = ActiveSheet.UsedRange
    return rng
}

function get_context(task)
{
    let context = {}

    let targetWorksheet = ActiveSheet
    let targetWorkbook = ActiveWorkbook
    let currentRange = GetActiveRange()
    let targetRange;
    if (task.column)
        targetRange = currentRange.Columns(task.column)
    else if (task.range)
        targetRange = Range(task.range)
    
    return [task, currentRange, context]
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
    "DISAGGREGATION_SEPARATOR": """
    DisaggregationSeparator(currentRange, task, task.separatorList, 0, context)
    """,
    "DISAGGREGATION_TEXTTYPE": """
    DisaggregationTextType(currentRange, task, task.typeList, 1, context)
    """,
    "DISAGGREGATION_KEYWORD": """
    DisaggregationKeyword(currentRange, task, task.keyList, 2, context)
    """,
    "DISAGGREGATION_LENGTH": """
    DisaggregationLength(currentRange, task, task.lengthList, 3, context)
    """
}


FUNCTIONS = {
"DisaggregationSeparator":"""function DisaggregationSeparator(currentRange, task, keyList, type, context)
{
    if(typeof(task.key) != "undefined" && task.key.length > 0)
    {
        let opRange = Range(task.key + ":" + task.key)
        let tableRange = GetTableRangeFromKey(context, task.key)
        
        if(!task.splitHeader) //不拆分表头
        {
            opRange = opRange.Rows(`2:${tableRange.Rows.Count}`)
        }
        else{
            opRange = opRange.Rows(`1:${tableRange.Rows.Count}`)
        }

        let dRange = opRange
        try{ dRange = Range(task.dRange) } catch (e) {}
        if (!dRange)
            dRange = opRange
        let  qType = 0;
        if(Array.isArray(keyList) && keyList.length == 1){
            keyList =  processFullHalfForms(keyList);
        }
        if(task.isSmart != null && (task.isSmart == true || task.isSmart == 'true')){
            var disObj = {type : 0, list : []}
            GetDataType(opRange, disObj);
            type = disObj.type
            keyList = disObj.list
        }
        if(task.QualifierType != null){
            qType = parseInt(task.QualifierType)
        }

        let bKeepKeyWord = (undefined == task.bKeepKeyWord || !!task.bKeepKeyWord)
        let bAfterKeyWord = (undefined == task.bAfterKeyWord || !!task.bAfterKeyWord)

        if(opRange && dRange)
        {   
            opRange.RangeEx.DataSmartSplitEx(dRange, keyList, type, qType, bKeepKeyWord, bAfterKeyWord)
        }

        if(typeof(task.displayType) != "undefined")
        {
            opRange.NumberFormatLocal = GetNumberFormatType(task.displayType)   
        }
    }
}       
    """,
"DisaggregationTextType":"""function DisaggregationTextType(currentRange, task, keyList, type, context)
{
    if(typeof(task.key) != "undefined" && task.key.length > 0)
    {
        let opRange = Range(task.key + ":" + task.key)
        let tableRange = GetTableRangeFromKey(context, task.key)
        
        if(!task.splitHeader) //不拆分表头
        {
            opRange = opRange.Rows(`2:${tableRange.Rows.Count}`)
        }
        else{
            opRange = opRange.Rows(`1:${tableRange.Rows.Count}`)
        }

        let dRange = opRange
        try{ dRange = Range(task.dRange) } catch (e) {}
        if (!dRange)
            dRange = opRange
        let  qType = 0;
        let bKeepKeyWord = (undefined == task.bKeepKeyWord || !!task.bKeepKeyWord)
        let bAfterKeyWord = (undefined == task.bAfterKeyWord || !!task.bAfterKeyWord)

        if(opRange && dRange)
        {   
            opRange.RangeEx.DataSmartSplitEx(dRange, keyList, type, qType, bKeepKeyWord, bAfterKeyWord)
        }

        if(typeof(task.displayType) != "undefined")
        {
            opRange.NumberFormatLocal = GetNumberFormatType(task.displayType)   
        }
    }
}
    """,
"DisaggregationKeyword":"""function DisaggregationKeyword(currentRange, task, keyList, type, context)
{
    if(typeof(task.key) != "undefined" && task.key.length > 0)
    {
        let opRange = Range(task.key + ":" + task.key)
        let tableRange = GetTableRangeFromKey(context, task.key)
        
        if(!task.splitHeader) //不拆分表头
        {
            opRange = opRange.Rows(`2:${tableRange.Rows.Count}`)
        }
        else{
            opRange = opRange.Rows(`1:${tableRange.Rows.Count}`)
        }

        let dRange = opRange
        try{ dRange = Range(task.dRange) } catch (e) {}
        if (!dRange)
            dRange = opRange
        let  qType = 0;
        let bKeepKeyWord = (undefined == task.bKeepKeyWord || !!task.bKeepKeyWord)
        let bAfterKeyWord = (undefined == task.bAfterKeyWord || !!task.bAfterKeyWord)

        if(opRange && dRange)
        {   
            opRange.RangeEx.DataSmartSplitEx(dRange, keyList, type, qType, bKeepKeyWord, bAfterKeyWord)
        }

        if(typeof(task.displayType) != "undefined")
        {
            opRange.NumberFormatLocal = GetNumberFormatType(task.displayType)   
        }
    }
}
    """,
"DisaggregationLength":"""function DisaggregationLength(currentRange, task, keyList, type, context)
{
    if(typeof(task.key) != "undefined" && task.key.length > 0)
    {
        let opRange = Range(task.key + ":" + task.key)
        let tableRange = GetTableRangeFromKey(context, task.key)
        
        if(!task.splitHeader) //不拆分表头
        {
            opRange = opRange.Rows(`2:${tableRange.Rows.Count}`)
        }
        else{
            opRange = opRange.Rows(`1:${tableRange.Rows.Count}`)
        }

        let dRange = opRange
        try{ dRange = Range(task.dRange) } catch (e) {}
        if (!dRange)
            dRange = opRange

        if(typeof(task.wordCount) != "undefined" && task.wordCount > 0)
            keyList = getLengthListByWordCount(opRange, task.wordCount)
        else if(keyList != null && keyList.length > 0){
            processLengthList(keyList);
        }
        let  qType = 0;
        let bKeepKeyWord = (undefined == task.bKeepKeyWord || !!task.bKeepKeyWord)
        let bAfterKeyWord = (undefined == task.bAfterKeyWord || !!task.bAfterKeyWord)

        if(opRange && dRange)
        {   
            opRange.RangeEx.DataSmartSplitEx(dRange, keyList, type, qType, bKeepKeyWord, bAfterKeyWord)
        }

        if(typeof(task.displayType) != "undefined")
        {
            opRange.NumberFormatLocal = GetNumberFormatType(task.displayType)   
        }
    }
}
""",

"GetNumberFormatType":"""function GetNumberFormatType(type)
{
    let ret = "G/通用格式" //常规
    switch (type) {
        case 0:
            ret = "G/通用格式"
            break;
        case 1:
            ret = "0.00_);[红色](0.00)";
            break;
        case 2:
            ret = "￥#,##0.00_);[红色](￥#,##0.00)";
            break;
        case 3:
            ret = "_ \\"￥\\"* #,##0.00_ ;_ \\"￥\\"* \\-#,##0.00_ ;_ \\"￥\\"* \\"-\\"??_ ;_ @_ ";
            break;  
        case 4:
            ret = "yyyy/m/d;@";
            break;  
        case 5:
            ret = "h:mm:ss;@";
            break;  
        case 6:
            ret = "0.00%";
            break;
        case 7:
            ret = "# ?/?";
            break;
        case 8:
            ret = "0.00E+00";
            break;
        case 9:
            ret = "@"
            break;    
        default:
            break;
    }
    return ret
}
    """,
"processLengthList":"""function processLengthList(lengthList)
{
    let br = false
    for(let i = 0; i < lengthList.length - 1; ++i){
        if(lengthList[i] >= lengthList[i + 1]){
            br = true;
            break;
        }
    }
    if(br){
        for(i = 1; i < lengthList.length; ++i){
            let curValue = lengthList[i]
            lengthList[i] = lengthList[i - 1] + curValue
        }
    }
}
    """,
"getLengthListByWordCount":"""function getLengthListByWordCount(range, wordCnt)
{
    let  maxLen = 0;
    for(let i = 1;i <= range.Rows.Count; i++){
        let len = range.Rows(i).Text.length
        if(len > maxLen)
            maxLen = len
    }

    let lenList = [wordCnt * 2]

    for(let i = 2; i * wordCnt < maxLen; i++){
        lenList.push(wordCnt * 2 * i);
    }
    return lenList;
}
""",
"processFullHalfForms":"""function processFullHalfForms(keyList)
{
    if(keyList.length != 1)
        return;
    if(keyList[0] == "；" || keyList[0] == ";")
        keyList = ["；",";"]
    else  if(keyList[0] == "," || keyList[0] == "，")
        keyList = [",","，"]
    return keyList
}
""",
"isLetter":"""function isLetter(ch)
{
    const pattern2 = new RegExp("[A-Za-z]+");
    return pattern2.test(ch);
}
""",
"isNumberChar":"""function isNumberChar(ch) 
{
    return ch >= '0' && ch <= '9'|| ch >= '０' && ch <= '９';
}
""",
"isChinese":"""function isChinese(ch)
{
    return ch.charCodeAt() >= 0x4E00 && ch.charCodeAt() <= 0x9FA5;
}""",
"GetAddressKeyWords":"""function GetAddressKeyWords()
{
    let address  = ['省', '市', '区', '县', '乡', '镇']
    return address;
}
""",
"GetRowWeightAndType":"""function GetRowWeightAndType(strText, weightMap, similarType, obj)
{
    let preType = -1;
    let curType = -1;
    let addrCnt = 0;
    let typeCnt = 0;
    let adressKey  = GetAddressKeyWords();
    let characterArray  = [];  //当前行已经插入过的字符，只算一次权重
    
    const TT_CHINESE = 0;          // 中文
    const TT_ENGLISH = 1;          // 英文
    const TT_NUMBER = 2;           // 数字
    const TT_SYMBOL = 3;             // 符号
    const Weight_Level1 = 10;        // 中文权重
    const Weight_Level2 = 50;        // 符号权重

    for(let i = 0; i < strText.length; ++i){
        let  ch = strText[i];
        
        if (isLetter(ch))
        {
            curType = TT_ENGLISH;
        }
        else if (isNumberChar(ch))
        {
            curType = TT_NUMBER;
        }
        else if (isChinese(ch))
        {
            curType = TT_CHINESE;
            
            if(characterArray.indexOf(ch) == -1){
                if(weightMap.has(ch)){
                    let value = weightMap.get(ch);
                    value += Weight_Level1;
                    weightMap.set(ch, value)
                }
                else{
                    weightMap.set(ch, Weight_Level1)
                }
            }

            if (addrCnt < 2   &&  adressKey.indexOf(ch) != -1)
            {
                obj.addrWeight += Weight_Level1;
                ++addrCnt;
            }
        }
        else
        {
            if(characterArray.indexOf(ch) == -1){
                if(weightMap.has(ch)){
                    let value = weightMap.get(ch);
                    value += Weight_Level2;
                    weightMap.set(ch, value)
                }
                else{
                    weightMap.set(ch, Weight_Level2)
                }
            }
        }
        characterArray.push(ch)
        if (curType != preType){
            typeCnt++;
            if(!obj.bMuitlType && typeCnt >= 2)
                obj.bMuitlType = true;
                
            let  len =  similarType.length;
            if(similarType.length == 0){
                similarType.push(curType)
            }
            else{
                if(similarType[len -1 ] != curType){
                    similarType.push(curType)
                }
            }
            preType = curType;
        }
    }
}
""",
"GetDataType":"""function GetDataType(range, disObj)
{
    const Weight_Level1 = 10;        // 中文
    const Weight_Level2 = 50;        // 符号
    
    var weightMap = new Map();
    let callCount = 0;
    let similarType = [];
    
    var obj = {"bMuitlType":false, "addrWeight":0}
    
    let i = 1;
     for(;i <= range.Rows.Count; i++){
         let text = range.Rows(i).Text
         
         if(i == 1)
         {
          GetRowWeightAndType(text, weightMap, similarType, obj)
         }
         else{
             let otherType = []
             GetRowWeightAndType(text, weightMap, otherType, obj)
             
             //从第二行开始如果拿出来顺序和第一行不末端，则删除按文本的顺序
             let k = 0;
             for(; k < similarType.length && k < otherType.length; k++){
                 if(similarType[k] != otherType[k]){
                     similarType.splice(k, similarType.length - k)
                     break;
                 }
             }
         }
    }
    
    let DelimiterBound = Weight_Level2 * i * 0.7;
    let KeyWordUBound = Weight_Level1 * i;
    let KeyWordLBound = Weight_Level1 * i * 0.7;
    let AddressBound = Weight_Level1 * 2 * i * 0.7;
    
    let adressKey  = GetAddressKeyWords();
    
    let vecDelimiters = [];
    let setKeyWords = [];
    let setAddresses = [];
    let bHasSpace = false;
    let addressesCnt = 0;
    for (const [key, value] of weightMap)
    {
        if (value >= DelimiterBound)
        {
            if ('\"' == key)
                continue;
            if (' ' == key)
                bHasSpace = true;
            vecDelimiters.push(key);
        }
        else if (isChinese(key))
        {
            if (KeyWordLBound <=  value && value <= KeyWordUBound)
            {
                setKeyWords.push(key);
            }
            if (addressesCnt < 5 && adressKey.indexOf(key) != -1)  //地址的最多五个
            {
                setAddresses.push(key);
                ++addressesCnt;
            }
        }
    }
    
    
    if (vecDelimiters.length != 0)
    {
        if (bHasSpace && obj.bMultiType && similarType.length != 0)
        {
            let bLetter = false;
            for (const ch of similarType)
            {
                if (TT_ENGLISH == it)
                {
                    bLetter = true;
                    break;
                }
            }
            if (bLetter)
            {
                disObj.type = 1;
                disObj.list = similarType;
                return
            }
        }

        let maxDelimiters = 6;
        if(vecDelimiters.length > maxDelimiters){
            vecDelimiters.splice(maxDelimiters, vecDelimiters.length - maxDelimiters)
        }
        disObj.type = 0;
        disObj.list = vecDelimiters;
        return
    }
    
    
    if (0 != AddressBound && obj.addrWeight >= AddressBound)
    {
        disObj.type = 2;
        disObj.list = setAddresses;
        return
    }
    
    if (obj.bMultiType && similarType.length != 0)
    {
        disObj.type = 1;
        disObj.list = similarType;
        return
        
    }

    if (callCount > 1 && !setKeyWords.empty())
    {
        disObj.type = 2;
        disObj.list = setKeyWords;
        return
    }
    disObj.type = 0;
    disObj.list = [".",",", ";", "“","”","!"," ", "\t"];
}
""",
"GetTableRangeFromKey":"""function GetTableRangeFromKey(context, key)
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
"dis_get_context":"""function dis_get_context(task)
{
    let context = {}

    let targetWorksheet = ActiveSheet
    let targetWorkbook = ActiveWorkbook
    let currentRange = GetActiveRange()
    let targetRange;
    if (task.column)
        targetRange = currentRange.Columns(task.column)
    else if (task.range)
        targetRange = Range(task.range)
    
    return [task, currentRange, context]
}"""

}

# 工具函数和对应依赖函数列表
DISAGGREGATION_MAPS = {
    "DisaggregationSeparator": ["DisaggregationSeparator", "processFullHalfForms", "GetTableRangeFromKey", "GetRowWeightAndType", "GetNumberFormatType", 
                                "isChinese", "GetAddressKeyWords", "isLetter", "isNumberChar", "GetDataType", "GetActiveRange", "dis_get_context"],
    "dis_get_context": ["dis_get_context"]
}