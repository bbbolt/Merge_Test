CONTEXT_CODE = """

function get_context(task)
{
    let targetWorksheet = ActiveSheet
    let targetWorkbook = ActiveWorkbook

    return [task, targetWorksheet, targetWorkbook]
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
    "HYBERLINK_INSERT": """
    HyberLinkInsert(targetWorksheet, targetWorkbook, task)
    """,
    "HYBERLINK_DELETE": """
    HyberLinkDelete(targetWorksheet, task)
    """,
    "HYBERLINK_OPEN": """
    HyberLinkOpen(targetWorksheet, task)
    """,
    "HYBERLINK_INSERT_2SHEETS": """
    HyberLink2Sheets(targetWorksheet, task)
    """
}


FUNCTIONS = {
"HyberLinkInsert":"""function HyberLinkInsert(targetWorksheet, targetWorkbook, task)
{
    let curWorksheet = GetHyberLinkSheet(targetWorksheet, task)
    let curRange = GetHyberLinkSelRange(curWorksheet, task)
    if(task.Address == undefined)
    {
        task.Address = ""
    }
    if(task.SubAddress == undefined)
    {
        task.SubAddress = ""
    }
    if(task.Type == 2 && task.key != undefined && task.RefSheetName != undefined)
    {
        let cellRange = findRangeByContent(task.RefSheetName, task.key, 1, xlPart)
        if(cellRange.length > 0)
        {
            let addr = Cells(cellRange[0][0], cellRange[0][1]).Address(false,false)
            task.SubAddress = task.RefSheetName + "!" + addr
        }
    }
    if (task.Type == 4)
    {
        let docPath = targetWorkbook.Path
        if (docPath == "")
        {
            docPath = Env.GetDesktopPath()
        }
        let pathSeparator = docPath.includes("\\\\") ? "\\\\" : "/"
        let bShowDifferentText = task.Address == task.LinkText
        task.Address = docPath + pathSeparator + task.Address
        if (bShowDifferentText)
            task.LinkText = docPath + pathSeparator + task.LinkText
    }
    // 一次为每个单元格设置链接，避免链接显示设置失败
    for (let i = 1; i <= curRange.Count; i++)
    {
        let item = curRange.Cells.Item(i)
        item.Hyperlinks.Add(item, task.Address, task.SubAddress, (task.ScreenTip == undefined ? "" : task.ScreenTip), task.LinkText)
    }
    curRange.Select()
}
""",
"GetHyberLinkSheet":"""function GetHyberLinkSheet(targetWorksheet, task)
{
    let curWorksheet = targetWorksheet
    try
    {
        curWorksheet = Application.Sheets.Item(task.SheetName)
    }
    catch (e) {}
    if (!curWorksheet)
        curWorksheet = targetWorksheet
    curWorksheet.Activate()
    return curWorksheet
}""",

"GetHyberLinkSelRange":"""function GetHyberLinkSelRange(targetWorksheet, task)
{
    let curRange = null
    try
    {
        curRange = targetWorksheet.Range(task.SelRange)
    }
    catch (e)
    {
        targetWorksheet.Activate()
        curRange = Selection
    }
    return curRange
}
""",
"findRangeByContent":"""function findRangeByContent(sheetName, key, count, lookAt)
{
    let curSheet = ActiveSheet
    if(typeof(sheetName) != "undefined" && sheetName.length > 0)
        curSheet = Sheets.Item(sheetName);
    
    let curUsedRange = curSheet.UsedRange;
    let findrg = curUsedRange.Find(key, undefined, -4176, lookAt, xlByRows, xlNext, false, false, true);
    if(findrg == null)
        return null;
    let startCol = findrg.Column 
    let startRow = findrg.Row
    var arrRange = [[findrg.Row,findrg.Column]]

    do
    {
        findrg = curUsedRange.FindNext(findrg)
        if(findrg == null)
            break;
        if(startCol == findrg.Column && startRow == findrg.Row)
            break;
        
        if(count > 0 && arrRange.length == count)
        {
            break;
        }
        arrRange.push([findrg.Row,findrg.Column])
    }while(1);    
    return arrRange
}""",
"HyberLinkDelete":"""function HyberLinkDelete(targetWorksheet, task)
{
    let curWorksheet = GetHyberLinkSheet(targetWorksheet, task)
    let curRange = GetHyberLinkSelRange(curWorksheet, task)
    curRange.Hyperlinks.Delete()
    curRange.Select()
}""",
"HyberLinkOpen":"""function HyberLinkOpen(targetWorksheet, task)
{
    let curWorksheet = GetHyberLinkSheet(targetWorksheet, task)
    let curRange = GetHyberLinkSelRange(curWorksheet, task)
    if(curRange.Hyperlinks.Count > 0)
    {
        curRange.Hyperlinks.Item(1).Follow(undefined, undefined, undefined, undefined, undefined)
    }
    curRange.Select()
}
""",
"HyberLink2Sheets":"""function HyberLink2Sheets(targetWorksheet, task)
{
    let curWorksheet = GetHyberLinkSheet(targetWorksheet, task)
    let curRange = GetHyberLinkSelRange(curWorksheet, task)
    let refWorksheet = GetHyberLinkRefSheet(targetWorksheet, task)
    let offsetRange = refWorksheet.Range(task.OffsetRange == undefined ? curRange.Cells.Item(1).Address() : task.OffsetRange)

    for (let i = 1; i <= curRange.Rows.Count; i++)
    {
        for (let j = 1; j <= curRange.Columns.Count; j++)
        {
            let item = curRange.Cells.Item(i, j)
            let subAddress = refWorksheet.Name + "!" + offsetRange.Offset(i - 1, j - 1).Address()
            let linkText = task.LinkText
            if (linkText == undefined || linkText.length <= 0)
                linkText = subAddress
            
            item.Hyperlinks.Add(item, "", subAddress, (task.ScreenTip == undefined ? "" : task.ScreenTip), linkText)
        }
    }
}
""",
"GetHyberLinkRefSheet":"""function GetHyberLinkRefSheet(targetWorksheet, task)
{
    let refWorksheet = targetWorksheet
    try
    {
        refWorksheet = Application.Sheets.Item(task.RefSheetName)
    }
    catch(e) {}
    if (!refWorksheet)
        refWorksheet = targetWorksheet
    return refWorksheet
}
""",
"get_context":"""function get_context(task)
{
    let targetWorksheet = ActiveSheet
    let targetWorkbook = ActiveWorkbook

    return [task, targetWorksheet, targetWorkbook]
}"""

}