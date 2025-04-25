CONTEXT_CODE = """

function get_context(task)
{
    let context = {}

    context.structArray = task
    let tableRange = ActiveSheet.UsedRange

    let targetWorksheet = ActiveSheet
    let currentRange = ActiveSheet.UsedRange
    let targetRange;

    try
    {
        if (task.column)
            targetRange = currentRange.Columns(task.column)
        else if (task.range)
            targetRange = Range(task.range)
        else
            targetRange = currentRange
    } catch {
        return false;
    }

    return [tableRange,targetRange,currentRange] //返回数据
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
    'CLOP_AUTOFITROW': 'CLOPAutofitRow',
    'CLOP_AUTOFITCOL': 'CLOPAutofitCol',

    "CLOP_COLWIDTH": "CLOPColWidth",
    "CLOP_ROWHEIGHT": "CLOPRowHeight",
    "CLOP_ROWHEIGHTSPECIFIC": "CLOPRowHeightSpecific",
    "CLOP_STANDARDWIDTH": "CLOPStandardWidth",
    "CLOP_DELETECOL": "CLOPDeleteCol",
    "CLOP_DELETEROW": "CLOPDeleteRow",
    "CLOP_CHANGEVISIBLE": "CLOPChangeVisible",
    "CLOP_COLUMNSINSERT": "CLOPColumnsInsert",
    "CLOP_ROWSINSERT": "CLOPRowsInsert",
    "CLOP_PASTE": "CLOPPaste",
    "CLOP_COPY": "CLOPCopy",
    "CLOP_CELLMOVE": "CLOPCellMove",
    "CLOP_CUT": "CLOPCut",
    "CLOP_CUTPASTE": "CLOPCutPaste",
    "CLOP_ROWSMOVE": "CLOPRowsMove",
    "CLOP_COLUMNSMOVE": "CLOPColumnsMove",
    "CLOP_EXCHANGECOL": "CLOPExchangeCol",
    "CLOP_EXCHANGEROW": "CLOPExchangeRow",
    "CLOP_FINDREPLACE": "CLOPFindReplace",
    "CLOP_COLORREPLACE": "CLOPColorReplace",
    "CLOP_ASSIGNMENT": "CLOPAssignment",

    "CLOP_CONCAT": "CLOPConcat",
    "CLOP_CALCULATE": "CLOPCalculate",
    "CLOP_DELETEVALUE": "CLOPDeleteValue",
    "CLOP_SPECIALSELECT": "CLOPSpecialSelect",
    "CLOP_DELETESPECIALCELL": "CLOPDeleteSpecialCell",
    "CLOP_LOCATIONREPLACE": "CLOPLocationReplace",
    "CLOP_EXCHANGERANGE": "CLOPExchangeRange",

    "SetColWidth": "SetColWidth",
    "GetXlPasteType": "GetXlPasteType",
    "GetPasteOperator": "GetPasteOperator",
    "SetRowHeight": "SetRowHeight",
    "FindDelete": "FindDelete",
    "FindContentDo": "FindContentDo",
    "FindColorDo": "FindColorDo",
    "FindChangeVisible": "FindChangeVisible",
    "GetSpecialCellEnum": "GetSpecialCellEnum",
    "FindReplace": "FindReplace",
    "FindReplaceColor": "FindReplaceColor",
    "exchangeColumn": "exchangeColumn",
    "exchangeRow": "exchangeRow",
    "GetColumnRowRange": "GetColumnRowRange",
    "RowExchange": "RowExchange",
    "CutInsertRow": "CutInsertRow",
    "RowMove": "RowMove",
    "InsertNullRowOrCol": "InsertNullRowOrCol",
    "CheckEmptyRowOrColumn": "CheckEmptyRowOrColumn",
    "rangeAssignment": "rangeAssignment",
    "ConcatCellsValue": "ConcatCellsValue",
    "CalculateCellsValue": "CalculateCellsValue",
    "DeleteCellsValue": "DeleteCellsValue",
    "GetCellTypeEnum": "GetCellTypeEnum",
    "specialSelect": "specialSelect",
    "DeleteSpecialCell": "DeleteSpecialCell",
    "FindCellDo": "FindCellDo",
    "locationReplace": "locationReplace",
    "exchangeRange": "exchangeRange",
    "GetUnionTableRange": "GetUnionTableRange",

    "IsCellAddress": "IsCellAddress",
    "findRangeByContent": "findRangeByContent",

    "FindContent": "FindContent",  # 新加查找内容
    "CLOP_FIND": "CLOPFind",  # 新加类
    "Find": "Find",

}
# 函数名字映射


# 函数内容映射
FUNCTIONS_MAP = {

    "CLOP_AUTOFITROW": """
        CLOPAutofitRow(tableRange,targetRange,currentRange, task)
    """,

    "CLOP_AUTOFITCOL": """
        CLOPAutofitCol(tableRange,targetRange,currentRange, task)
    """,

    "CLOP_COLWIDTH": "CLOPColWidth(tableRange,targetRange,currentRange, task)",
    "CLOP_ROWHEIGHT": "CLOPRowHeight(tableRange,targetRange,currentRange, task)",
    "CLOP_ROWHEIGHTSPECIFIC": "CLOPRowHeightSpecific(tableRange,targetRange,currentRange, Task)",
    "CLOP_STANDARDWIDTH": "CLOPStandardWidth(tableRange,targetRange,currentRange, Task)",
    "CLOP_DELETECOL": "CLOPDeleteCol(tableRange,targetRange,currentRange, Task)",
    "CLOP_DELETEROW": "CLOPDeleteRow(tableRange,targetRange,currentRange, task)",
    "CLOP_CHANGEVISIBLE": "CLOPChangeVisible(tableRange,targetRange,currentRange, task)",
    "CLOP_COLUMNSINSERT": "CLOPColumnsInsert(tableRange,targetRange,currentRange, task)",
    "CLOP_ROWSINSERT": "CLOPRowsInsert(tableRange,targetRange,currentRange, task)",
    "CLOP_PASTE": "CLOPPaste(tableRange,targetRange,currentRange, task)",
    "CLOP_COPY": "CLOPCopy(tableRange,targetRange,currentRange, task)",
    "CLOP_CELLMOVE": "CLOPCellMove(tableRange,targetRange,currentRange, task)",
    "CLOP_CUT": "CLOPCut(tableRange,targetRange,currentRange, task)",
    "CLOP_CUTPASTE": "CLOPCutPaste(tableRange,targetRange,currentRange, task)",
    "CLOP_ROWSMOVE": "CLOPRowsMove(tableRange,targetRange,currentRange, task)",
    "CLOP_COLUMNSMOVE": "CLOPColumnsMove(tableRange,targetRange,currentRange, task)",
    "CLOP_EXCHANGECOL": "CLOPExchangeCol(tableRange,targetRange,currentRange, task)",
    "CLOP_EXCHANGEROW": "CLOPExchangeRow(tableRange,targetRange,currentRange, task)",
    "CLOP_FINDREPLACE": "CLOPFindReplace(tableRange,targetRange,currentRange, task)",
    "CLOP_COLORREPLACE": "CLOPColorReplace(tableRange,targetRange,currentRange, task)",
    "CLOP_ASSIGNMENT": "CLOPAssignment(tableRange,targetRange,currentRange, task)",
    "CLOP_CONCAT": "CLOPConcat(tableRange,targetRange,currentRange, task)",
    "CLOP_CALCULATE": "CLOPCalculate(tableRange,targetRange,currentRange, task)",
    "CLOP_DELETEVALUE": "CLOPDeleteValue(tableRange,targetRange,currentRange, task)",
    "CLOP_SPECIALSELECT": "CLOPSpecialSelect(tableRange,targetRange,currentRange, task)",
    "CLOP_DELETESPECIALCELL": "CLOPDeleteSpecialCell(tableRange,targetRange,currentRange, task)",
    "CLOP_LOCATIONREPLACE": "CLOPLocationReplace(tableRange,targetRange,currentRange, task)",
    "CLOP_EXCHANGERANGE": "CLOPExchangeRange(tableRange,targetRange,currentRange, task)",

    "GetXlPasteType": "GetXlPasteType(type)",
    "GetPasteOperator": "GetPasteOperator(op)",
    "SetColWidth": "SetColWidth(task)",
    "SetRowHeight": "SetRowHeight(task)",
    "FindDelete": "FindDelete(targetRange, task, isRow)",
    "FindContentDo": "FindContentDo(currentRange, values, lookAt, doFunc)",
    "FindColorDo": "FindColorDo(currentRange, color_type, color, doFunc)",
    "FindChangeVisible": "FindChangeVisible(targetRange, currentRange, task)",
    "GetSpecialCellEnum": "GetSpecialCellEnum(str)",
    "FindReplace": "FindReplace(task)",
    "FindReplaceColor": "FindReplaceColor(targetRange, task)",
    "exchangeColumn": "exchangeColumn(col1, col2, tableRange)",
    "exchangeRow": "exchangeRow(row1, row2)",
    "GetColumnRowRange": "GetColumnRowRange(address, bColumn)",
    "RowExchange": "RowExchange(currentRange, task)",
    "CutInsertRow": "CutInsertRow(rows1, rows2, isMoveAfter)",
    "RowMove": "RowMove(currentRange, task)",
    "FindRowsInsert": "FindRowsInsert(task)",
    "InsertNullRowOrCol": "InsertNullRowOrCol(range, count, isRow, isFront, interval)",
    "CheckEmptyRowOrColumn": "CheckEmptyRowOrColumn(srcRange, cellRange, isRow)",
    "rangeAssignment": "rangeAssignment(task)",
    "ConcatCellsValue": "ConcatCellsValue(targetRange, task)",
    "CalculateCellsValue": "CalculateCellsValue(targetRange, task)",
    "DeleteCellsValue": "DeleteCellsValue(targetRange, task)",
    "GetCellTypeEnum": "GetCellTypeEnum(type)",
    "specialSelect": "specialSelect(targetRange, task)",
    "DeleteSpecialCell": "DeleteSpecialCell(targetRange, task)",
    "FindCellDo": "FindCellDo(currentRange, doFunc)",
    "locationReplace": "locationReplace(targetRange, task)",
    "exchangeRange": "exchangeRange(currentRange, task)",

    "GetUnionTableRange": "GetUnionTableRange(tableInfos)",
    "IsCellAddress": "IsCellAddress(str)",
    "findRangeByContent": "findRangeByContent(sheetName, key, count, lookAt)",

    "CLOP_FIND": "CLOPFind(tableRange,targetRange,currentRange, task)",
    "Find_Content": "FindContent(currentRange, values, lookAt)",
    "Find": "Find(task)",

    # 'GetColumnRowRange':"GetColumnRowRange(address, bColumn)",
    # "FindDelete":"FindDelete(targetRange, task, isRow)",
    # "SetColWidth":"SetColWidth(task)",
    # "SetRowHeight":"SetRowHeight(task)",
    # "FindChangeVisible":"FindChangeVisible(targetRange, currentRange, task)",
    # "InsertNullRowOrCol":"InsertNullRowOrCol",
    # "FindRowsInsert":"FindRowsInsert(range, count, isRow, isFront, interval)",
    # "GetXlPasteType":"GetXlPasteType(type)",
    # "GetPasteOperator":"GetPasteOperator(op)",
    # "exchangeColumn":"exchangeColumn(col1, col2, tableRange)",
    # "RowExchange":"RowExchange(currentRange, task)",
    # "FindReplace":"FindReplace(task)",
    # "FindReplaceColor":"FindReplaceColor(targetRange, task)"
    # "rangeAssignment":"rangeAssignment(task)"
    # "ConcatCellsValue":"ConcatCellsValue(targetRange, task)",
    # "CalculateCellsValue":"CalculateCellsValue(targetRange, task)",
    # "DeleteCellsValue":"DeleteCellsValue(targetRange, task)",
    # "specialSelect":"specialSelect(targetRange, task)",
    # "DeleteSpecialCell":"DeleteSpecialCell(targetRange, task)",
    # "locationReplace":"locationReplace(targetRange, task)",
    # "exchangeRange":"exchangeRange(currentRange, task)",
    # "":"",

}

COMMON_FUNC_LST = [
    "IllegalStringParameter",
    "IllegalBooleanParameter"
]

"""
TASK2FUNC_MAP 不变
FUNCTIONS_MAP 函数值变
FUNCTIONS 变


"""

COMMON_CODE = '''
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

    "CLOPAutofitRow": '''function CLOPAutofitRow(tableRange,targetRange,currentRange, task){GetColumnRowRange(task.rows, false).AutoFit()}''',

    "CLOPAutofitCol": """function  CLOPAutofitCol(tableRange,targetRange,currentRange, task){GetColumnRowRange(task.cols, true).AutoFit()}""",

    "CLOPColWidth": """function CLOPColWidth(tableRange,targetRange,currentRange,task){SetColWidth(task)}""",

    "CLOPRowHeight": """function CLOPRowHeight(tableRange,targetRange,currentRange,task){SetRowHeight(task)}""",

    "RowHeightSpecificCLOP": """
function RowHeightSpecificCLOP(tableRange,targetRange,currentRange,task){
    let height = -1
    try { height = parseFloat(task.height) } catch { height = -1 }
    let specific = -1
    try { specific = parseFloat(task.specific) } catch { specific = -1 }
    if (height > 0 && specific > 0)
    {
        let rows = GetColumnRowRange(task.rows, false);
        for (let i = 1; i <= rows.Count; ++i)
        {
            if (rows.Item(i).RowHeight == specific)
                rows.Item(i).RowHeight = height
        }
    }
    else
    {
        GetColumnRowRange(task.rows, false).AutoFit()
    }


}
""",

    "CLOPStandardWidth": "function CLOPStandardWidth(tableRange,targetRange,currentRange,task){Worksheets(task.sheetName).StandardWidth = parseFloat(task.width)}",

    "CLOPDeleteCol": """
function CLOPDeleteCol(tableRange,targetRange,currentRange,task){ 
    let range = ActiveSheet.UsedRange
    try { range = Range(task.cols) } catch {
        range = Columns(task.cols)
    }
    FindDelete(range, task, false)
}
""",

    "CLOPDeleteRow": """
function CLOPDeleteRow(tableRange,targetRange,currentRange,task){
    let range = ActiveSheet.UsedRange
    try { range = Range(task.rows) } catch {
        range = Rows(task.rows)
    }
    FindDelete(range, task, true)
}""",

    "CLOPChangeVisible": "function CLOPChangeVisible(tableRange,targetRange,currentRange,task){FindChangeVisible(targetRange, currentRange, task)}",
    "CLOPColumnsInsert": """
function CLOPColumnsInsert(tableRange,targetRange,currentRange,task){
    let interval = task.interval == undefined ? 1 : task.interval + 1
    InsertNullRowOrCol(GetColumnRowRange(task.ref_cols, true), task.num, false, task.position == "xlBefore", interval)
}""",

    "CLOPRowsInsert": "function CLOPRowsInsert(tableRange,targetRange,currentRange,task){FindRowsInsert(task)}",

    "CLOPPaste": """
function CLOPPaste(tableRange,targetRange,currentRange,task){
    let paste_type = task.paste_type != undefined ? GetXlPasteType(task.paste_type) : xlPasteAll
    let operator = task.operator != undefined ? GetPasteOperator(task.operator) : xlPasteSpecialOperationNone
    let bSkipBlanks = task.bSkipBlanks != undefined ? task.bSkipBlanks : false
    let bTranspose = task.bTranspose != undefined ? task.bTranspose : false
    if (task.bPicture)
    {
        targetRange.Select()
        targetWorksheet.PasteSpecial("图片(Windows元文件)")
    }
    else if (task.bText)
    {
        targetRange.Select()
        ActiveSheet.PasteSpecial("无格式文本")
    }
    else
    {
        targetRange.PasteSpecial(paste_type, operator, bSkipBlanks, bTranspose)
    }
}""",

    "CLOPCopy": "function CLOPCopy(tableRange,targetRange,currentRange,task){targetRange.Copy()}",

    "CLOPCellMove": """
function CLOPCellMove(tableRange,targetRange,currentRange,task){
    if (typeof (task.src_cell) == 'string')
        task.src_cell = task.src_cell.replace(/\*/g, '')
    if (typeof (task.ref_cell) == 'string')
        task.ref_cell = task.ref_cell.replace(/\*/g, '')
    if (task.src_cell == "" || task.ref_cell == "")
        return

    let rangeSrc = Range(task.src_cell)
    rangeSrc.Cut(null)
    let rangeRef = Range(task.ref_cell)
    rangeRef.Select()
    ActiveSheet.Paste(null, null)
}""",

    "CLOPCut": "function CLOPCut(tableRange,targetRange,currentRange,task){targetRange.Cut()}",

    "CLOPCutPaste": """
function CLOPCutPaste(tableRange,targetRange,currentRange,task){
    targetRange.Select()
    ActiveSheet.Paste()
}""",

    "CLOPRowsMove": "function CLOPRowsMove(tableRange,targetRange,currentRange,task){ RowMove(currentRange, task)}",

    "CLOPColumnsMove": """
function CLOPColumnsMove(tableRange,targetRange,currentRange,task){
    let cutRange = Application.Intersect(tableRange, GetColumnRowRange(task.src_cols, true));
    cutRange.Cut(null)
    let insertRange = Application.Intersect(tableRange, GetColumnRowRange(task.ref_col, true))
    if (task.position == "xlAfter")
    {
        insertRange = insertRange.Offset(0, 1)
    }
    insertRange.Insert(xlRight, xlFormatFromRightOrBelow);
}""",

    "CLOPExchangeCol": """
function CLOPExchangeCol(tableRange,targetRange,currentRange,task){
    let cols1 = GetColumnRowRange(task.cols1, true)
    let cols2 = GetColumnRowRange(task.cols2, true)
    exchangeColumn(cols1, cols2, tableRange)
}""",
    "CLOPExchangeRow": "function CLOPExchangeRow(tableRange,targetRange,currentRange,task){ RowExchange(currentRange, task)}",
    "CLOPFindReplace": "function CLOPFindReplace(tableRange,targetRange,currentRange,task){FindReplace(task)}",
    "CLOPColorReplace": """
function CLOPColorReplace(tableRange,targetRange,currentRange,task){
    targetRange = Application.Intersect(tableRange, targetRange);
    FindReplaceColor(targetRange, task)
}""",

    "CLOPAssignment": "function CLOPAssignment(tableRange,targetRange,currentRange,task){rangeAssignment(task)}",
    "CLOPConcat": "function CLOPConcat(tableRange,targetRange,currentRange,task){ConcatCellsValue(targetRange, task)}",
    "CLOPCalculate": "function CLOPCalculate(tableRange,targetRange,currentRange,task){CalculateCellsValue(targetRange, task)}",
    "CLOPDeleteValue": "function CLOPDeleteValue(tableRange,targetRange,currentRange,task){ DeleteCellsValue(targetRange, task)}",
    "CLOPSpecialSelect": "function CLOPSpecialSelect(tableRange,targetRange,currentRange,task){specialSelect(targetRange, task)}",
    "CLOPDeleteSpecialCell": "function CLOPDeleteSpecialCell(tableRange,targetRange,currentRange,task){ DeleteSpecialCell(targetRange, task)}",
    "CLOPLocationReplace": "function CLOPLocationReplace(tableRange,targetRange,currentRange,task){locationReplace(targetRange, task)}",
    "CLOPExchangeRange": "function CLOPExchangeRange(tableRange,targetRange,currentRange,task){exchangeRange(currentRange, task)}",

    "GetColumnRowRange": '''
function GetColumnRowRange(address, bColumn)
{
    if (bColumn)
    {
        try { return Columns(address) }
        catch { return Range(address).EntireColumn; }
    }
    else
    {
        try { return Rows(address) }
        catch { return Range(address).EntireRow; }
    }
}
''',

    "FindDelete": """
function FindDelete(targetRange, task, isRow){
    let currentRange = Intersect(targetRange, ActiveSheet.UsedRange)
    if (task.is_delete_blank)
    {
        let blankRanges = []
        if (isRow)
        {
            let rowCount = currentRange.Rows.Count
            if (rowCount > 7000 && MsgBox("需要处理的区域较大，可能需要耗时几分钟、甚至更久。\\n是否继续？",jsOKCancel) != 1)
                return
            let rowStart = currentRange.Row
            for (let i = rowStart + rowCount - 1; i >= rowStart; --i)
            {
                let countBlank = WorksheetFunction.CountA(Rows(i));
                if (countBlank == 0)
                    blankRanges.push(Rows(i))
            }
        }
        else
        {
            let colCount = currentRange.Columns.Count
            if (colCount > 5000 && MsgBox("需要处理的区域较大，可能需要耗时几分钟、甚至更久。\\n是否继续？",jsOKCancel) != 1)
                return
            let colStart = currentRange.Column
            for (let i = colStart + colCount - 1; i >= colStart; --i)
            {
                let countBlank = WorksheetFunction.CountA(Columns(i));
                if (countBlank == 0)
                    blankRanges.push(Columns(i))
            }
        }
        if (blankRanges.length != 0) {
            let needDeleteRanges = blankRanges[0]
            for (let i = 1; i < blankRanges.length; i++)
                needDeleteRanges = Union(needDeleteRanges, blankRanges[i])
            needDeleteRanges.Delete()
        }
        return
    }

    if (task.is_delete_hidden)
    {
        let blankRanges = []
        if (isRow)
        {
            let rowCount = currentRange.Rows.Count
            if (rowCount > 7000 && MsgBox("需要处理的区域较大，可能需要耗时几分钟、甚至更久。\\n是否继续？",jsOKCancel) != 1)
                return
            let rowStart = currentRange.Row
            for (let i = rowStart + rowCount - 1; i >= rowStart; --i)
            {
                if (Rows(i).Hidden)
                    blankRanges.push(Rows(i))
            }
        }
        else
        {
            let colCount = currentRange.Columns.Count
            if (colCount > 5000 && MsgBox("需要处理的区域较大，可能需要耗时几分钟、甚至更久。\\n是否继续？",jsOKCancel) != 1)
                return
            let colStart = currentRange.Column
            for (let i = colStart + colCount - 1; i >= colStart; --i)
            {
                if (Columns(i).Hidden)
                    blankRanges.push(Columns(i))
            }
        }
        if (blankRanges.length != 0) {
            let needDeleteRanges = blankRanges[0]
            for (let i = 1; i < blankRanges.length; i++)
                needDeleteRanges = Union(needDeleteRanges, blankRanges[i])
            needDeleteRanges.Delete()
        }
        return
    }

    if (task.delete_values != undefined && task.delete_values.length > 0)
    {
        if (task.delete_cols != undefined)
            currentRange = Application.Intersect(currentRange, GetColumnRowRange(task.delete_cols, true))
        for (let i = 0; i < task.delete_values.length; i++)
        {
            if (task.delete_values[i] != null)
            {
                let xlLookAt = 2
                if (task.find_entire != undefined && task.find_entire == true)
                {
                    xlLookAt = 1
                }
                let value = task.delete_values[i]
                let cellResult = currentRange.Find(value, null, -4176, xlLookAt, 1, 1, 0, 0, true)
                while (cellResult != undefined)
                {
                    if (isRow)
                        cellResult.EntireRow.Delete()
                    else
                        cellResult.EntireColumn.Delete()
                    cellResult = currentRange.Find(value, null, -4176, xlLookAt, 1, 1, 0, 0, true)
                }
            }
            else
            {
                const srcfirstRow = currentRange.Row
                const srclastRow = currentRange.Row + currentRange.Rows.Count - 1
                const srcfirstCol = currentRange.Column
                const srclastCol = currentRange.Column + currentRange.Columns.Count - 1

                if (isRow)
                {
                    let cell1 = ActiveSheet.Cells(srcfirstRow, srcfirstCol)
                    let cell2 = ActiveSheet.Cells(srcfirstRow, srclastCol)
                    let startRange = Range(cell1, cell2)
                    let iterRange = startRange
                    for (let i = srcfirstRow; i <= srclastRow; i++)
                    {
                        if (CheckEmptyRowOrColumn(iterRange, cell1, isRow))
                        {
                            let temp = iterRange.Offset(1, 0)
                            cell1 = cell1.Offset(1, 0)
                            iterRange.EntireRow.Delete()
                            iterRange = temp
                        }
                        else
                        {
                            iterRange = iterRange.Offset(1, 0)
                            cell1 = cell1.Offset(1, 0)
                        }
                    }
                }
                else
                {
                    let cell1 = ActiveSheet.Cells(srcfirstRow, srcfirstCol)
                    let cell2 = ActiveSheet.Cells(srclastRow, srcfirstCol)
                    let startRange = Range(cell1, cell2)
                    let iterRange = startRange
                    for (let i = srcfirstCol; i <= srclastCol; i++)
                    {
                        if (CheckEmptyRowOrColumn(iterRange, cell1, isRow))
                        {
                            let temp = iterRange.Offset(0, 1)
                            cell1 = cell1.Offset(0, 1)
                            iterRange.EntireColumn.Delete()
                            iterRange = temp
                        }
                        else
                        {
                            iterRange = iterRange.Offset(0, 1)
                            cell1 = cell1.Offset(0, 1)
                        }
                    }
                }
            }
        }
    }
    else if (task.rows || task.cols)
    {
        if (isRow)
            targetRange.EntireRow.Delete()
        else
        targetRange.EntireColumn.Delete()
    }
}


""",

    "GetXlPasteType": '''
function GetXlPasteType(type)
{
    switch (type)
    {
        case "xlPasteAll":
            return -4104
        case "xlPasteAllExceptBorders":
            return 7
        case "xlPasteAllMergingConditionalFormats":
            return 14
        case "xlPasteAllUsingSourceTheme":
            return 13
        case "xlPasteColumnWidths":
            return 8
        case "xlPasteComments":
            return -4144
        case "xlPasteFormats":
            return -4122
        case "xlPasteFormulas":
            return -4123
        case "xlPasteFormulas|xlPasteNumberFormats":
        case "xlPasteFormulasAndNumberFormats":
            return 11
        case "xlPasteValidation":
            return 6
        case "xlPasteValues":
            return -4163
        case "xlPasteValues|xlPasteNumberFormats":
        case "xlPasteValuesAndNumberFormats":
            return 12
        default:
            return xlPasteAll
    }
}
''',

    "GetPasteOperator": '''
function GetPasteOperator(op)
{
    switch (op)
    {
        case '+':
            return xlPasteSpecialOperationAdd
        case '-':
            return xlPasteSpecialOperationSubtract
        case '\*':
            return xlPasteSpecialOperationMultiply
        case '/':
            return xlPasteSpecialOperationDivide
        default:
            return xlPasteSpecialOperationNone
    }
}
''',

    "SetColWidth": '''
function SetColWidth(task)
{
    let ref_arg = 0
    try { ref_arg = parseFloat(task.ref_arg) } catch {
        GetColumnRowRange(task.cols, true).AutoFit()
        return
    }
    if (task.ref_col == "self")
    {
        let cols = GetColumnRowRange(task.cols, true);
        for (let i = 1; i <= cols.Count; ++i)
        {
            if (task.ref_operator == "+")
                cols.Columns(i).ColumnWidth += ref_arg
            else
                cols.Columns(i).ColumnWidth *= ref_arg
        }
    }
    else
    {
        let width = -1
        try { width = parseFloat(task.width) } catch { width = -1 }
        if (task.ref_col != undefined)
        {
            width = GetColumnRowRange(task.ref_col, true).ColumnWidth
            if (ref_arg != undefined)
            {
                if (task.ref_operator == "+")
                    width = width + ref_arg
                else
                    width = width * ref_arg
            }
        }
        if (width > 0)
            GetColumnRowRange(task.cols, true).ColumnWidth = width
        else
            GetColumnRowRange(task.cols, true).AutoFit()
    }
}
''',

    "SetRowHeight": '''
function SetRowHeight(task)
{
    let ref_arg = 0
    try { ref_arg = parseFloat(task.ref_arg) } catch {
        GetColumnRowRange(task.rows, false).AutoFit()
        return
    }
    if (task.ref_row == "self")
    {
        let rows = GetColumnRowRange(task.rows, false);
        for (let i = 1; i <= rows.Count; ++i)
        {
            if (task.ref_operator == "+")
                rows.Item(i).RowHeight += ref_arg
            else
                rows.Item(i).RowHeight *= ref_arg
        }
    }
    else
    {
        let height = -1
        try { height = parseFloat(task.height) } catch { height = -1 }
        if (task.ref_row != undefined)
        {
            height = GetColumnRowRange(task.ref_row, false).RowHeight
            if (task.ref_operator == "+")
                height = height + ref_arg
            else
                height = height * ref_arg
        }
        if (height > 0)
            GetColumnRowRange(task.rows, false).RowHeight = height
        else
            GetColumnRowRange(task.rows, false).AutoFit()
    }
}
''',

    "FindContentDo": '''
//枚举values的值，调用doFunc；doFunc返回false则中断
function FindContentDo(currentRange, values, lookAt, doFunc)
{
    for (let i = 0; i < values.length; ++i)
    {
        let value = values[i]
        let cellResult = currentRange.Find(value, null, -4176, lookAt, 1, 1, 0, 0, true)
        if (cellResult == undefined)
            continue;

        let firstCell = cellResult.Address()
        while (cellResult != undefined)
        {
            // 需要在替换之前选中单元格，否则按照WPS的替换逻辑会造成替换区域错误
            cellResult.Select()
            if (!doFunc(cellResult))
                return
            cellResult = currentRange.Find(value, cellResult, -4176, lookAt, 1, 1, 0, 0, true)
            if (cellResult == undefined || firstCell == cellResult.Address())
                break
        }
    }
}
''',

    "FindColorDo": '''
function FindColorDo(currentRange, color_type, color, doFunc)
{
    let cellResult = currentRange.Find("", null, xlFormulas, xlPart, xlByRows, xlNext, 0, 0, true)
    if (cellResult == undefined)
        return

    let firstCell = cellResult.Address()
    while (cellResult)
    {
        cellResult.Select()
        if (!doFunc(cellResult))
            return
        // 此处与FindContentDo保持一致，以cellResult为起始单元格，否则赋值文本后会由于允许没有内容限制重复查找到已经修改过的单元格
        cellResult = currentRange.Find("", cellResult, xlFormulas, xlPart, xlByRows, xlNext, 0, 0, true)
        if (cellResult == undefined || firstCell == cellResult.Address())
            break
    }
}

''',

    "FindChangeVisible": '''
function FindChangeVisible(targetRange, currentRange, task)
{
    if (typeof (task.value) == 'string')
        task.value = [task.value]
    function setHidden(cellResult, isRow = task.isRow, visible = task.visible)
    {
        if (isRow)
            cellResult.EntireRow.Hidden = !visible
        else
            cellResult.EntireColumn.Hidden = !visible
        return true
    }
    function setHiddenExcept(cellResult, isRow = task.isRow, visible = task.visible, except = task.except)
    {
        if (typeof (except) == 'string')
            except = except.replace(/\*/g, '')
        if (except == "")
            return
        arr = except.split(",")
        if (isRow)
        {
            for (let i = 1; i < cellResult.Rows.Count; ++i)
            {
                let isExcept = false;
                for (let j = 0; j < arr.length; ++j)
                {
                    let src = cellResult.Rows(i).Row
                    let ref = Rows(arr[j]).Row
                    if (src == ref)
                    {
                        isExcept = true
                        break;
                    }
                }
                if (isExcept)
                    continue
                cellResult.Rows(i).EntireRow.Hidden = !visible
            }
        }
        else
        {
            for (let i = 1; i < cellResult.Columns.Count; ++i)
            {
                let isExcept = false;
                for (let j = 0; j < arr.length; ++j)
                {
                    let src = cellResult.Columns(i).Column
                    let ref = Columns(arr[j]).Column
                    if (src == ref)
                    {
                        isExcept = true
                        break;
                    }
                }
                if (isExcept)
                    continue
                cellResult.Columns(i).EntireColumn.Hidden = !visible
            }
        }
        return true
    }

    if (task.value != undefined && task.value.length > 0 && task.value[0] != '')
        FindContentDo(currentRange, task.value, xlPart, setHidden)
    else if (task.except != undefined && task.except.length > 0 && task.except[0] != '')
        setHiddenExcept(targetRange)
    else
        setHidden(targetRange)
}

''',

    "GetSpecialCellEnum": '''
function GetSpecialCellEnum(str)
{
    switch (str)
    {
        case "xlNumbers":
            return xlNumbers
        case "xlTextValues":
            return xlTextValues
        case "xlLogical":
            return xlLogical
        case "xlErrors":
            return xlErrors
        case "xlNonNumbers":
            return xlErrors + xlLogical + xlTextValues
        default:
            return 0
    }
}
''',

    "FindReplace": '''
function FindReplace(task)
{
    let celltype = GetSpecialCellEnum(task.src_value)
    let lookAt = task.find_mode == "xlCellValue" ? xlWhole : xlPart

    function doReplaceSpCell(range, isEntireRow = true, type = celltype, des = task.des_value)
    {
        if (isEntireRow)
            range = range.EntireRow
        try { range.SpecialCells(xlCellTypeConstants, type).Formula = des } catch { }
        try { range.SpecialCells(xlCellTypeFormulas, type).Formula = des } catch { }
        return true
    }
    function doReplaceRow(range, obj = task, look = lookAt)
    {
        let cellRange = range.EntireRow
        FindContentDo(cellRange, [obj.src_value], look, doReplaceCell)
        return --obj.replace_count
    }
    function doReplaceCell(range, obj = task)
    {
        if (obj.replace_mode == "xlWhole")
        {
            range.Formula = obj.des_value
            return --obj.replace_count
        }
        range.Replace(obj.src_value,obj.des_value, xlPart, xlByRows, false, false, true, true)
        return --obj.replace_count
    }
    function doReplaceBefore(range, obj = task)
    {
        let txt = range.Value2
        let index = txt.indexOf(obj.src_value);
        if (index != -1)
        {
            if (obj.replace_mode == "xlBeforeSelf")
                range.Value2 = obj.des_value + txt.substring(index + 1)
            else
                range.Value2 = obj.des_value + txt.substring(index)
        }
        return --obj.replace_count
    }
    function doReplaceAfter(range, obj = task)
    {
        let txt = range.Value2
        let index = txt.indexOf(obj.src_value);
        if (index != -1)
        {
            if (obj.replace_mode == "xlAfterSelf")
                range.Value2 = txt.substring(0, index) + obj.des_value
            else
                range.Value2 = txt.substring(0, index + 1) + obj.des_value
        }
        return --obj.replace_count
    }

    if (task.replace_mode == "xlBefore" || task.replace_mode == "xlBeforeSelf")
    {
        FindContentDo(Range(task.where), [task.src_value], lookAt, doReplaceBefore)
        return
    }
    else if (task.replace_mode == "xlAfter" || task.replace_mode == "xlAfterSelf")
    {
        FindContentDo(Range(task.where), [task.src_value], lookAt, doReplaceAfter)
        return
    }

    if (celltype != 0)
    {
        if (!IsCellAddress(task.where))
            FindContentDo(ActiveSheet.UsedRange, [task.where], lookAt, doReplaceSpCell)
        else
            doReplaceSpCell(Range(task.where), false)
    }
    else
    {
        if (!IsCellAddress(task.where))
        {
            if (null == task.where)
                FindContentDo(ActiveSheet.UsedRange, [task.src_value], lookAt, doReplaceCell)
            else
                FindContentDo(ActiveSheet.UsedRange, [task.where], lookAt, doReplaceRow)
        }
        else
        {
            FindContentDo(Range(task.where), [task.src_value], lookAt, doReplaceCell)
        }
    }
}
''',

    "FindReplaceColor": '''
function FindReplaceColor(targetRange, task)
{
    function doReplaceValueColor(range, obj = task)
    {
        // 查找内容和替换内容保证统一防止修改内容
        range.Replace(obj.src_value, obj.src_value, xlPart, xlByRows, false, false, false, true);
        return --obj.replace_count
    }

    function doReplaceColor(range, obj = task)
    {
        range.Replace("", "", xlPart, xlByRows, false, false, true, true);
        return --obj.replace_count
    }

    function doReplaceCell(range, obj = task)
    {
        // 对单元格内容进行全部替换
        range.Value2 = obj.des_value
        return --obj.replace_count
    }

    if (task.isAllWorkbook)
    {
        let originalSheet = ActiveSheet
        for (let i = 1; i <= Sheets.Count; i++)
        {
            targetRange = Sheets(i).UsedRange.CurrentRegion
            Sheets(i).Activate()

            if (task.des_value_type == "value")
            {
                // 若是设值文字，则调用doReplaceCell用于替换查找到的区域中的内容
                if (task.src_value_type == "value")
                    FindContentDo(targetRange, [task.src_value], xlPart, doReplaceCell)
                else
                    FindColorDo(targetRange, task.src_value_type, task.src_value, doReplaceCell)
            }
            else
            {
                if (task.src_value_type == "value")
                    FindContentDo(targetRange, [task.src_value], xlPart, doReplaceValueColor)
                else
                    FindColorDo(targetRange, task.src_value_type, task.src_value, doReplaceColor)
            }
        }
        originalSheet.Activate()
    }
    else
    {
        if (task.des_value_type == "value")
        {
            // 逻辑与上述一致
            if (task.src_value_type == "value")
                FindContentDo(targetRange, [task.src_value], xlPart, doReplaceCell)
            else
                FindColorDo(targetRange, task.src_value_type, task.src_value, doReplaceCell)
        }
        else
        {
            if (task.src_value_type == "value")
                FindContentDo(targetRange, [task.src_value], xlPart, doReplaceValueColor)
            else
                FindColorDo(targetRange, task.src_value_type, task.src_value, doReplaceColor)
        }
    }

    Application.FindFormat.Clear()
    Application.ReplaceFormat.Clear()
}
''',

    "exchangeColumn": '''
function exchangeColumn(col1, col2, tableRange)
{
    let bLarge = col1.Column > col2.Column
    let col1End = col1.Column + col1.Columns.Count - 1
    let col2End = col2.Column + col2.Columns.Count - 1
    let columnOffset = bLarge ? col2End - col1.Column + 1 : col1End - col2.Column + 1
    if (columnOffset > 0)
        return
    let tableRangeEntireRow = tableRange.Rows.EntireRow
    col1 = Application.Intersect(tableRangeEntireRow, col1)
    col2 = Application.Intersect(tableRangeEntireRow, col2)
    if (!bLarge)
    {
        let colTarget = Application.Intersect(tableRangeEntireRow, col2.Offset(0, col2.Columns.Count))
        col2.Cut(null)
        col1.Insert(xlRight, xlFormatFromRightOrBelow);
        col1.Cut(null)
        colTarget.Insert(xlRight, xlFormatFromRightOrBelow);
    }
    else
    {
        let colTarget = Application.Intersect(tableRangeEntireRow, col1.Offset(0, col1.Columns.Count))
        col1.Cut(null)
        col2.Insert(xlRight, xlFormatFromRightOrBelow);
        col2.Cut(null)
        colTarget.Insert(xlRight, xlFormatFromRightOrBelow);
    }
}
''',

    "exchangeRow": '''
function exchangeRow(row1, row2)
{
    let bLarge = row1.Row > row2.Row
    let row1End = row1.Row + row1.Rows.Count - 1
    let row2End = row2.Row + row2.Rows.Count - 1
    let rowOffset = bLarge ? row2End - row1.Row + 1 : row1End - row2.Row + 1
    if (rowOffset > 0)
        return
    if (!bLarge)
    {
        let rowTarget = row2.Offset(row2.Rows.Count, 0)
        row2.Cut(null)
        row1.Insert(xlBottom)
        row1.Cut(null)
        rowTarget.Insert(xlBottom)
    }
    else
    {
        let rowTarget = row1.Offset(row1.Rows.Count, 0)
        row1.Cut(null)
        row2.Insert(xlBottom)
        row2.Cut(null)
        rowTarget.Insert(xlBottom)
    }
}
''',

    "RowExchange": '''
function RowExchange(currentRange, task)
{
    if (typeof (task.value1) == "string")
        task.value1 = task.value1.replace(/\*/g, '')
    if (typeof (task.value2) == "string")
        task.value2 = task.value2.replace(/\*/g, '')
    if (task.value1 == "" || task.value2 == "")
        return

    let rows1, rows2
    if (task.value2_type == "xlCellValue")
        rows2 = currentRange.Find(task.value2, null, -4176, xlWhole, 1, 0, 0, true)
    else if (task.value2_type == "xlCellValuePart")
        rows2 = currentRange.Find(task.value2, null, -4176, xlPart, 1, 0, 0, true)
    else
        rows2 = GetColumnRowRange(task.value2, false)

    if (task.value1_type == "xlCellValue")
        rows1 = currentRange.Find(task.value1, null, -4176, xlWhole, 1, 0, 0, true)
    else if (task.value1_type == "xlCellValuePart")
        rows1 = currentRange.Find(task.value1, null, -4176, xlPart, 1, 0, 0, true)
    else
        rows1 = GetColumnRowRange(task.value1, false)

    if (rows1 == undefined || rows2 == undefined)
        return

    exchangeRow(rows1.EntireRow, rows2.EntireRow)
}
''',

    "CutInsertRow": '''
function CutInsertRow(rows1, rows2, isMoveAfter)
{
    rows1.EntireRow.Cut(null)
    if (isMoveAfter)
        rows2.Offset(1, 0).EntireRow.Insert(xlDown, xlFormatFromRightOrBelow)
    else//moveTo 和moveBefore其实是一样的
        rows2.EntireRow.Insert(xlDown, xlFormatFromLeftOrAbove)
}
''',

    "RowMove": '''
function RowMove(currentRange, task)
{
    if (typeof (task.src_value) == 'string')
        task.src_value = task.src_value.replace(/\*/g, '')
    if (typeof (task.ref_value) == 'string')
        task.ref_value = task.ref_value.replace(/\*/g, '')
    if (task.src_value == "" || task.ref_value == "")
        return

    let rows1, rows2
    if (task.ref_type == "xlCellValue")
        rows2 = currentRange.Find(task.ref_value, null, -4176, xlWhole, 1, 0, 0, true)
    else if (task.ref_type == "xlCellValuePart")
        rows2 = currentRange.Find(task.ref_value, null, -4176, xlPart, 1, 0, 0, true)
    else
        rows2 = GetColumnRowRange(task.ref_value, false)

    if (rows2 == undefined) return
    let isMoveAfter = task.position == "xlAfter"
    if (task.src_type == "xlRowIndex" || task.src_type == undefined)
    {
        rows1 = GetColumnRowRange(task.src_value, false)
        CutInsertRow(rows1, rows2, isMoveAfter)
        return
    }

    const startRow = rows2.Row
    let lookAt = task.src_type == "xlCellValue" ? xlWhole : xlPart
    let col = currentRange.Find(task.src_value, null, -4176, lookAt, 1, 0, 0, true)
    if (col == undefined) return
    if (!isMoveAfter)
    {
        const RowCount = currentRange.Row + currentRange.Rows.Count - 1
        let iterCell = Cells(rows2.Row + 1, col.Column)
        for (let i = startRow + 1; i <= RowCount; ++i)
        {
            if (iterCell.Value2 == task.src_value)
            {
                let temp = iterCell.Offset(1, 0)
                CutInsertRow(iterCell, rows2, isMoveAfter)
                iterCell = temp
            }
            else
            {
                iterCell = iterCell.Offset(1, 0)
            }
        }
    }
    else if (startRow > 1)
    {
        let iterCell = Cells(rows2.Row - 1, col.Column)
        for (let i = startRow - 1; i > 0; --i)
        {
            if (iterCell.Value2 == task.src_value)
            {
                let temp
                if (iterCell.Row > 1)
                    temp = iterCell.Offset(-1, 0)
                CutInsertRow(iterCell, rows2, isMoveAfter)
                iterCell = temp
            }
            else if (iterCell.Row > 1)
            {
                iterCell = iterCell.Offset(-1, 0)
            }
        }
    }
}
''',

    "InsertNullRowOrCol": '''
function InsertNullRowOrCol(range, count, isRow, isFront, interval)
{
    if (count == undefined)
        count = 1;

    // 逻辑为从下或右往对侧插入新行或列，根据在前或后插入判断是否在第一行列前插入
    if (isRow)
    {
        format = xlFormatFromLeftOrAbove
        if (!isFront) {
            range = range.Offset(1, 0)
            format = xlFormatFromRightOrBelow
        }
        let rows = range.Rows
        let rowsCount = rows.Count

        // 若间隔插入的总数量不对，调整一下保证间隔从首行开始
        if (rowsCount % interval != 1 && interval != 1)
            rowsCount = rowsCount - (rowsCount % interval)
        if (rowsCount < interval)
            rowsCount = 1
        for (let nowRow = rowsCount; nowRow > 0; nowRow -= interval)
        {
            let row = rows(nowRow);
            for (let nowCount = 0; nowCount < count; nowCount++)
                row.EntireRow.Insert(xlDown, format);
        }
    }
    else
    {
        format = xlFormatFromLeftOrAbove
        if (!isFront) {
            range = range.Offset(0, 1)
            format = xlFormatFromRightOrBelow
        }
        let columns = range.Columns;
        let columnsCount = columns.Count

        if (columnsCount % interval != 1 && interval != 1)
            columnsCount = columnsCount - (columnsCount % interval)
        if (columnsCount < interval)
            columnsCount = 1
        for (let nowCol = columnsCount; nowCol > 0; nowCol -= interval)
        {
            let column = columns(nowCol);
            for (let nowCount = 0; nowCount < count; nowCount++)
                column.EntireColumn.Insert(xlRight, format);
        }
    }
}
''',

    "FindRowsInsert": '''
function FindRowsInsert(task)
{
    if (task.ref_value == "") return
    if (typeof (task.ref_value) == 'string')
        task.ref_value = task.ref_value.replace(/\*/g, '')

    let interval = task.interval == undefined ? 1 : task.interval
    let values = task.ref_value
    if (!Array.isArray(task.ref_value) && typeof (task.ref_value) != 'number')
        values = task.ref_value.split(',')

    // 当ref_type表示行号（默认行号）
    if (task.ref_type == "xlRowIndex" || task.ref_type == undefined)
    {
        for (let i = values.length - 1; i >= 0; --i)
            InsertNullRowOrCol(GetColumnRowRange(values[i], false), task.num, true, task.position == "xlBefore", interval)
        return
    }
    // 当ref_type表示条件公式
    if (task.ref_type == "xlFormula")
    {
        let dataArray = Application.Evaluate(task.ref_value)
        // 由ref_value的公式获取到行号
        let regex = /([A-Z]+)(\d+):([A-Z]+)(\d+)/;
        let match = task.ref_value.match(regex)
        let startRow = parseInt(match[2])
        // 对公式结果为True的行执行插入
        for (let i = dataArray.length - 1; i >= 0; i--)
            if (dataArray[i][0] == true)
                InsertNullRowOrCol(GetColumnRowRange(startRow + i, false), task.num, true, task.position == "xlBefore", interval)
        return
    }
    // 否则ref_type为查找对应或包含的内容的区域
    let lookAt = task.ref_type == "xlCellValue" ? xlWhole : xlPart
    let rowSet = new Set()
    for (let i = 0; i < values.length; ++i)
    {
        let ranges = findRangeByContent(ActiveSheet.Name, values[i], 0, lookAt, task.ref_cols)
        if (ranges != undefined)
            ranges.forEach(Element => rowSet.add(Element[0]))
    }
    const rowArray = Array.from(rowSet);
    for (let i = rowArray.length - 1; i >= 0; --i)
        InsertNullRowOrCol(GetColumnRowRange(rowArray[i], false), task.num, true, task.position == "xlBefore", interval)
}
''',

    "CheckEmptyRowOrColumn": '''
function CheckEmptyRowOrColumn(srcRange, cellRange, isRow)
{
    const srcfirstRow = srcRange.Row
    const srclastRow = srcRange.Row + srcRange.Rows.Count - 1
    const srcfirstCol = srcRange.Column
    const srclastCol = srcRange.Column + srcRange.Columns.Count - 1
    if (isRow)
    {
        const cellRow = cellRange.Row
        for (let i = srcfirstCol; i <= srclastCol; i++)
        {
            let cell = ActiveSheet.Cells(cellRow, i)
            if (cell.Value2 == "" || cell.Value2 == undefined)
                continue
            else
                return false
        }
    }
    else
    {
        const cellCol = cellRange.Column
        for (let i = srcfirstRow; i <= srclastRow; i++)
        {
            let cell = ActiveSheet.Cells(i, cellCol)
            if (cell.Value2 == "" || cell.Value2 == undefined)
                continue
            else
                return false
        }
    }
    return true
}
''',

    "angeAssignment": '''
function rangeAssignment(task)
{
    let targetRange = task.range == undefined ? ActiveCell : Range(task.range)

    // 删除内容操作，clear字段true:清除内容及格式/false or undefined:清空内容
    if (task.content == "")
    {
        if (task.clearFormat)
            targetRange.Clear()
        else
            targetRange.Value2 = ""
    }
    // 内容替换操作
    else if (task.content != undefined)
    {
        targetRange.Value2 = task.content
    }
}
''',

    "ConcatCellsValue": '''
function ConcatCellsValue(targetRange, task)
{
    let endRow = ActiveSheet.UsedRange.Row + ActiveSheet.UsedRange.Rows.Count
    let endColumn = ActiveSheet.UsedRange.Column + ActiveSheet.UsedRange.Columns.Count
    let rowCount = targetRange.Row + targetRange.Rows.Count < endRow ? targetRange.Rows.Count : endRow - targetRange.Row
    let columnCount = targetRange.Column + targetRange.Columns.Count < endColumn ? targetRange.Columns.Count : endColumn - targetRange.Column
    let content = null
    if (task.content_type == "range")
    {
        try{    let contentRange = Range(task.content)} catch { return }
        let contentRange = Range(task.content)
        if (contentRange.Rows.Count == 1 && contentRange.Columns.Count == 1)
            content = contentRange.Cells.Item(1, 1).Value2
        else
        {
            for (let i = 1; i <= rowCount; i++)
            {
                for (let j = 1; j <= columnCount; j++)
                {
                    if (contentRange.Cells.Item(i, j).Value2 != null)
                    {
                        if (targetRange.Cells.Item(i, j).Value2 == null)
                        {
                            targetRange.Cells.Item(i, j).Value2 = contentRange.Cells.Item(i, j).Value2
                        }
                        else
                        {
                            if (task.position == "xlAfter")
                                targetRange.Cells.Item(i, j).Value2 = targetRange.Cells.Item(i, j).Value2 + contentRange.Cells.Item(i, j).Value2
                            else if (task.position == "xlBefore")
                                targetRange.Cells.Item(i, j).Value2 = contentRange.Cells.Item(i, j).Value2 + targetRange.Cells.Item(i, j).Value2
                        }
                    }
                }
            }
        }
    }
    else
        content = task.content
    if (content != null)
    {
        for (let i = 1; i <= rowCount; i++)
        {
            for (let j = 1; j <= columnCount; j++)
            {
                if (targetRange.Cells.Item(i, j).Value2 == null)
                {
                    targetRange.Cells.Item(i, j).Value2 = content
                }
                else
                {
                    if (task.position == "xlAfter")
                        targetRange.Cells.Item(i, j).Value2 = targetRange.Cells.Item(i, j).Value2 + content
                    else if (task.position == "xlBefore")
                        targetRange.Cells.Item(i, j).Value2 = content + targetRange.Cells.Item(i, j).Value2
                }
            }
        }
    }
}
''',

    "CalculateCellsValue": '''
function CalculateCellsValue(targetRange, task)
{
    let endRow = ActiveSheet.UsedRange.Row + ActiveSheet.UsedRange.Rows.Count
    let endColumn = ActiveSheet.UsedRange.Column + ActiveSheet.UsedRange.Columns.Count
    let rowCount = targetRange.Row + targetRange.Rows.Count < endRow ? targetRange.Rows.Count : endRow - targetRange.Row
    let columnCount = targetRange.Column + targetRange.Columns.Count < endColumn ? targetRange.Columns.Count : endColumn - targetRange.Column
    for (let i = 1; i <= rowCount; i++)
    {
        for (let j = 1; j <= columnCount; j++)
        {
            if (/^\d+(\.\d+)?$/.test(targetRange.Cells.Item(i, j).Value2))  //通过正则式判断单元格内容是否为纯数字
            {
                let value = parseFloat(targetRange.Cells.Item(i, j).Value2)
                switch (task.operator)
                {
                    case "+":
                        targetRange.Cells.Item(i, j).Value2 = value + task.argument
                        break
                    case "-":
                        targetRange.Cells.Item(i, j).Value2 = value - task.argument
                        break
                    case "*":
                        targetRange.Cells.Item(i, j).Value2 = value * task.argument
                        break
                    case "/":
                        targetRange.Cells.Item(i, j).Value2 = value / task.argument
                        break
                    default:
                        targetRange.Cells.Item(i, j).Value2 = value + task.argument
                }
            }
        }
    }
}
''',

    "DeleteCellsValue": '''
function DeleteCellsValue(targetRange, task)
{
    let endRow = ActiveSheet.UsedRange.Row + ActiveSheet.UsedRange.Rows.Count
    let endColumn = ActiveSheet.UsedRange.Column + ActiveSheet.UsedRange.Columns.Count
    let rowCount = targetRange.Row + targetRange.Rows.Count < endRow ? targetRange.Rows.Count : endRow - targetRange.Row
    let columnCount = targetRange.Column + targetRange.Columns.Count < endColumn ? targetRange.Columns.Count : endColumn - targetRange.Column
    for (let i = 1; i <= rowCount; i++)
    {
        for (let j = 1; j <= columnCount; j++)
        {
            if (targetRange.Cells.Item(i, j).Formula.length <= task.num)
            {
                targetRange.Cells.Item(i, j).Formula = null
            }
            else
            {
                if (task.position == "xlBefore")
                    targetRange.Cells.Item(i, j).Formula = targetRange.Cells.Item(i, j).Formula.slice(task.num)
                else if (task.position == "xlAfter")
                    targetRange.Cells.Item(i, j).Formula = targetRange.Cells.Item(i, j).Formula.slice(0, targetRange.Cells.Item(i, j).Formula.length - task.num)
            }
        }
    }
}
''',

    "GetCellTypeEnum": '''
function GetCellTypeEnum(type)
{
    switch (type)
    {
        case "xlCellTypeAllFormatConditions":
            return -4172
        case "xlCellTypeAllValidation":
            return -4174
        case "xlCellTypeBlanks":
            return 4
        case "xlCellTypeComments":
            return -4144
        case "xlCellTypeConstants":
            return 2
        case "xlCellTypeFormulas":
            return -4123
        case "xlCellTypeLastCell":
            return 11
        case "xlCellTypeSameFormatConditions":
            return -4173
        case "xlCellTypeSameValidation":
            return -4175
        case "xlCellTypeVisible":
            return 12
        default:
            return xlCellTypeAllFormatConditions
    }
}
''',

    "specialSelect": '''
function specialSelect(targetRange, task)
{
    // 根据不同的select_type选择整行或者整列或者单元格
    let type = GetCellTypeEnum(task.select_type)
    let cellValue = 0
    // 可能有二级定位条件
    if (type == xlCellTypeConstants || type == xlCellTypeFormulas)
        for(let i = 0; i < task.select_type_value.length; i++)
            cellValue += GetSpecialCellEnum(task.select_type_value[i])

    if (cellValue == 0)
    {
        if (task.select_range == "row")
            targetRange.SpecialCells(type).EntireRow.Select()
        else if (task.select_range == "col")
            targetRange.SpecialCells(type).EntireColumn.Select()
        else
            targetRange.SpecialCells(type).Select()
    }
    else
    {
        if (task.select_range == "row")
            targetRange.SpecialCells(type, cellValue).EntireRow.Select()
        else if (task.select_range == "col")
            targetRange.SpecialCells(type, cellValue).EntireColumn.Select()
        else
            targetRange.SpecialCells(type, cellValue).Select()
    }
}
''',

    "DeleteSpecialCell": '''
function DeleteSpecialCell(targetRange, task)
{
    let type = GetCellTypeEnum(task.delete_type)
    let cellValue = 0
    if (type == xlCellTypeConstants || type == xlCellTypeFormulas)
        for(let i = 0; i < task.delete_type_value.length; i++)
            cellValue += GetSpecialCellEnum(task.delete_type_value[i])
    if (cellValue == 0)
        targetRange.SpecialCells(type).Select()
    else
        targetRange.SpecialCells(type, cellValue).Select()

    if (task.shift_direction == "up")
        Selection.Delete(xlShiftUp);
    else
        Selection.Delete(xlShiftToLeft);
}
''',

    "FindCellDo": '''
function FindCellDo(currentRange, doFunc)
{
    // 找到currentRange中每个单元格执行doFunc操作
    let cellResult = currentRange.Find("*", null, xlFormulas, xlPart, xlByRows, xlNext, 0, 0, true)
    if (cellResult == undefined)
        return

    let firstCell = cellResult.Address()
    while (cellResult)
    {
        if (!doFunc(cellResult))
            return
        cellResult = currentRange.Find("*", cellResult, xlFormulas, xlPart, xlByRows, xlNext, 0, 0, true)
        if (cellResult == undefined || firstCell == cellResult.Address())
            break
    }
}
''',

    "locationReplace": '''
function locationReplace(targetRange, task)
{
    // range:处理区域-targetRange start_pos:开始位置 end_pos:结束位置 des_value:替换后字符 isRepeat:是否对每一位执行替换
    // 替换逻辑：
    // 1. start_pos > 0 end_pos >= 0 替换start_pos到end_pos的内容
    // 2. start_pos 无关 end_pos < 0 替换倒数到第-end_pos的内容
    // 3. start_pos > 0 end_pos 未定义 替换start_pos后全部的内容
    // 其他：替换某一位之前:start=0 end=n-1，替换某一位之后:start=n+1 end=undefined，倒数n项:end=-n，正数n项:start=0 end=n
    function doLocationReplace(range, obj = task)
    {
        let ref_value = range.Value2
        if (typeof (ref_value) != String)
            ref_value = range.Value2.toString()
        let replacedStr = ""
        let start_pos = obj.start_pos
        let end_pos = obj.end_pos
        let des_value = obj.des_value
        let isRepeat = obj.isRepeat

        // 从start_pos到end_pos替换
        if (obj.end_pos >= 0)
        {
            if (start_pos <= ref_value.length)
            {
                // 当end_pos在字符长度内
                if (end_pos <= ref_value.length)
                {
                    if (isRepeat)
                        replacedStr = ref_value.substring(0, start_pos - 1) + des_value.repeat(end_pos + 1 - start_pos) + ref_value.substring(end_pos)
                    else
                        replacedStr = ref_value.substring(0, start_pos - 1) + des_value + ref_value.substring(end_pos)
                }
                else
                {
                    if (isRepeat)
                        replacedStr = ref_value.substring(0, start_pos - 1) + des_value.repeat(ref_value.length + 1 - start_pos)
                    else
                        replacedStr = ref_value.substring(0, start_pos - 1) + des_value
                }
            }
            else
            {
                replacedStr = ref_value
            }
        }
        // 倒数end_pos位替换
        else if (obj.end_pos < 0)
        {
            if (-end_pos > ref_value.length)
            {
                if (isRepeat)
                    replacedStr = des_value.repeat(ref_value.length)
                else
                    replacedStr = des_value
            }
            else
            {
                if (isRepeat)
                    replacedStr = ref_value.slice(0, end_pos) + des_value.repeat(-end_pos)
                else
                    replacedStr = ref_value.slice(0, end_pos) + des_value
            }
        }
        // 从start_pos往后全部替换
        else if (obj.end_pos == undefined)
        {
            if (start_pos <= ref_value.length)
            {
                if (isRepeat)
                    replacedStr = ref_value.substring(0, start_pos - 1) + des_value.repeat(ref_value.length + 1 - start_pos)
                else
                    replacedStr = ref_value.substring(0, start_pos - 1) + des_value
            }
            else
            {
                replacedStr = ref_value
            }
        }

        range.Value2 = replacedStr
        return --obj.replace_count
    }

    FindCellDo(targetRange, doLocationReplace)
}
''',

    "exchangeRange": '''
function exchangeRange(currentRange, task)
{
    if (typeof (task.value1) == "string")
        task.value1 = task.value1.replace(/\*/g, '')
    if (typeof (task.value2) == "string")
        task.value2 = task.value2.replace(/\*/g, '')
    if (task.value1 == "" || task.value2 == "")
        return

    let rg1, rg2
    if (task.value2_type == "xlCellValue")
        rg2 = currentRange.Find(task.value2, null, -4176, xlWhole, 1, 0, 0, true)
    else if (task.value2_type == "xlCellValuePart")
        rg2 = currentRange.Find(task.value2, null, -4176, xlPart, 1, 0, 0, true)
    else
        rg2 = Range(task.value2)

    if (task.value1_type == "xlCellValue")
        rg1 = currentRange.Find(task.value1, null, -4176, xlWhole, 1, 0, 0, true)
    else if (task.value1_type == "xlCellValuePart")
        rg1 = currentRange.Find(task.value1, null, -4176, xlPart, 1, 0, 0, true)
    else
        rg1 = Range(task.value1)

    if (rg1 == undefined || rg2 == undefined)
        return

    let temp = rg1.Value2
    rg1.Value2 = rg2.Value2
    rg2.Value2 = temp
}
''',

    "GetUnionTableRange": '''
// 通过表结构识别获取用户所有的表单区域，表结构识别错误用整个工作表使用的区域，需要进行二次取交集
function GetUnionTableRange(tableInfos)
{
    let unionTableRange
    if (tableInfos != undefined && tableInfos.length > 0)
    {
        for (let i = 0; i < tableInfos.length; i++)
        {
            let tableInfo = tableInfos[i]
            if (unionTableRange == null)
                unionTableRange = Range(tableInfo.tableRange)
            else
                unionTableRange = Application.Union(Range(tableInfo.tableRange), unionTableRange)
        }
    }
    else
    {
        unionTableRange = ActiveSheet.UsedRange
    }

    return unionTableRange
}


''',

"IsCellAddress":
'''
function IsCellAddress(str){
    try{
        Range(str)
        return true
    }
    catch(e){return false}
}
''',

"findRangeByContent":
'''
//在sheetName这个表的usedRange范围内查找count个key对应的单元格，count <=0 表示全部查找
function findRangeByContent(sheetName, key, count, lookAt)
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
}
''',

    "FindContent": '''
//枚举values的值，调用doFunc；doFunc返回false则中断
function FindContent(currentRange, values, lookAt)
{
    let allFoundCells = [];
    for (let i = 0; i < values.length; ++i)
    {
        let value = values[i]
        let cellResult = currentRange.Find(value, null, -4176, lookAt, 1, 1, 0, 0, true)
        if (cellResult == undefined)
            continue;

        let firstCell = cellResult.Address()
        while (cellResult != undefined)
        {
            // 需要在替换之前选中单元格，否则按照WPS的替换逻辑会造成替换区域错误
            allFoundCells.push(cellResult);
            cellResult.Select(false)

            cellResult = currentRange.Find(value, cellResult, -4176, lookAt, 1, 1, 0, 0, true)
            if (cellResult == undefined || firstCell == cellResult.Address())
                break
        }
    }
    if (allFoundCells.length > 0) {
        // 选择所有找到的单元格
        var first = allFoundCells[0];
        for (let j = 1; j < allFoundCells.length; j++) {
            first = Application.Union(first, allFoundCells[j]);
        }
        first.Select();
    }
}
''',
    # 类
    "CLOPFind": "function CLOPFind(tableRange,targetRange,currentRange,task){Find(task)}",

    # 函数
    "Find": '''
function Find(task)
{
    let celltype = GetSpecialCellEnum(task.src_value)
    let lookAt = task.find_mode == "xlCellValue" ? xlWhole : xlPart

    if (celltype != 0)
    {
        if (!IsCellAddress(task.where))
            FindContent(ActiveSheet.UsedRange, [task.where], lookAt)
        else {
            let range = Range(task.where);
            FindContent(range.SpecialCells(xlCellTypeConstants, celltype), [task.src_value], lookAt);
            FindContent(range.SpecialCells(xlCellTypeFormulas, celltype), [task.src_value], lookAt);
        }
    }
    else
    {
        if (!IsCellAddress(task.where))
        {
            if (null == task.where)
                FindContent(ActiveSheet.UsedRange, [task.src_value], lookAt)
            else
                FindContent(ActiveSheet.UsedRange, [task.where], lookAt, (range) => {
                    FindContent(range.EntireRow, [task.src_value], lookAt);
                });
        }
        else
        {
            FindContent(Range(task.where), [task.src_value], lookAt)
        }
    }
}
'''

}
