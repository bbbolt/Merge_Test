# -*- coding: utf-8 -*-
# @Time : 2024/6/18 上午10:12
# @Author : sunyuzhao
# @Email : sunyuzhao@wps.cn
# @File : functions.py.py


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
    "doMerge": """
    doMerge(range, bAlignment)
    """,
    "doMergeContent": """
    doMergeContent(targetRange, bRemoveRepeat, separator, find_values)
    """,
    "RemoveDuplicates": """
    RemoveDuplicates(range)
    """,
    "FindMergeRange": """
    FindMergeRange(targetRange, find_values)
    """,
    "doMergeSame": """
    doMergeSame(targetRange, find_values)
    """,
    "FindMergeRangeSpecial": """
    FindMergeRangeSpecial(targetRange, value)
    """,
    "doMergeByRow": """doMergeByRow(range, bAlignment, bRow)""",
    "doMergeContentByRow": """doMergeContentByRow(range, bRow, bRemoveRepeat, separator, find_values)"""
}

FUNCTIONS = {
    "doMerge": """
function doMerge(range, bAlignment)
{
    range.Merge()
    if (bAlignment)
    {
        range.HorizontalAlignment = xlCenter
    }
}
""",
    "doMergeContent": """
function doMergeContent(targetRange, bRemoveRepeat, separator, find_values)
{
    Application.DisplayAlerts = false
    let rangeList = FindMergeRange(targetRange, find_values)
    if (rangeList.length <= 0)
            rangeList.push(targetRange)
      
    for (let i = 0; i < rangeList.length; i++)
    {
        let range = rangeList[i]
        if (bRemoveRepeat)
            RemoveDuplicates(range)
        try
        {
            range.RangeEx.MergeContent(separator)
        }
        catch
        {
            range.RangeEx.MergeContent()
        }
    }
    Application.DisplayAlerts = true
}""",

    "RemoveDuplicates": """function RemoveDuplicates(range)
{
    let length = range.Columns.Count
    let cols = Array.from({ length: length }, (item, index) => 1 + index)
    range.RemoveDuplicates(cols, xlNo)
}
""",
    "FindMergeRange": """function FindMergeRange(targetRange, find_values)
{
    var findResult = []
    if (!Array.isArray(find_values) || find_values.length <= 0)
        return findResult

    for (let i = 0; i < find_values.length; i++)
    {
        let value = find_values[i]
        if ("" === value)
            continue
        let cellResult = null
        if (undefined == value)
        {
            cellResult = FindMergeRangeSpecial(targetRange, value)
        }
        else
        {
            let cellFind = targetRange.Find(value, null, -4176, xlWhole, xlByRows, xlNext, 0, 0, true)
            if (cellFind == undefined)
                continue
            let firstCell = cellFind.Address()
            cellResult = cellFind
            while (cellFind != undefined)
            {
                cellFind = targetRange.Find(value, cellFind, -4176, xlWhole, xlByRows, xlNext, 0, 0, true)
                cellResult = Union(cellResult, cellFind)
                if (cellFind != undefined && firstCell == cellFind.Address())
                    break
            }
        }

        findResult.push(cellResult)
    }
    return findResult
}""",
    "doMergeSame": """function doMergeSame(targetRange, find_values)
{
    if (targetRange.Count > 10000)
    {
        if (MsgBox("您选择的区域比较大，合并相同单元格可能需要耗时几分钟、甚至更久。\\n是否继续？",jsOKCancel) != 1)
            return
    }
    Application.DisplayAlerts = false
    let findResult = FindMergeRange(targetRange, find_values)
    let values = []
    if (findResult.length <= 0 && find_values.length <= 0)
    {
        for (let i = 1; i <= targetRange.Rows.Count; i++)
        {
            for (let j = 1; j <= targetRange.Columns.Count; j++)
            {
                let value = targetRange.Cells.Item(i, j).Text
                if ("" === value || "0" === value)    // 若未指定合并内容，则区域内0和空白单元格视为相似单元格
                    values.push(undefined)
                else
            values.push(value)
            }
        }
        values = [...new Set(values)]
        find_values = values
        findResult = FindMergeRange(targetRange, find_values)
    }
        
    for (let i = 0; i < findResult.length; i++)
    {
        let range = findResult[i]
        range.RangeEx.MergeSame()
    }
    Application.DisplayAlerts = true
}""",
    "FindMergeRangeSpecial": """function FindMergeRangeSpecial(targetRange, value)
{
    let cellResult = null
    for (let i = 1; i <= targetRange.Rows.Count; i++)
    {
        for (let j = 1; j <= targetRange.Columns.Count; j++)
        {
            let cell = targetRange.Cells.Item(i, j)
            let cellFind = Range(cell.Address())
            let text = cell.Text
            if (undefined == value) // 相似单元格中空白单元格与0相同
            {
                if (!("" == text || "0" == text))
                    continue
            }
            else if (value != text)
            {
                continue
            }
            if (null == cellResult)
                cellResult = cellFind
            else
                cellResult = Union(cellResult, cellFind)
        }
    }
    return cellResult
}
""",
    "doMergeByRow": """function doMergeByRow(range, bAlignment, bRow)
{
    if (bRow)
    {
        range.Merge(true)
    }
    else
    {
        if (range.Columns.Count > 500)
        {
            if (MsgBox("您选择的区域比较大，合并单元格可能需要耗时几分钟、甚至更久。\\n是否继续？",jsOKCancel) != 1)
                return
        }
        for(let i=1 ; i<=range.Columns.Count;i++)
        {
            range.Columns(i).Merge()
        }
    }
    if (bAlignment)
    {
        range.HorizontalAlignment = xlCenter
        range.VerticalAlignment = xlCenter
    }
}
""",
    "doMergeContentByRow": """function doMergeContentByRow(range, bRow, bRemoveRepeat, separator, find_values)
{
    if (bRemoveRepeat)
        RemoveDuplicates(range)
    if(bRow)
    {
        if (range.Rows.Count > 5000)
        {
            if (MsgBox("您选择的区域比较大，合并单元格可能需要耗时几分钟、甚至更久。\\n是否继续？",jsOKCancel) != 1)
                return
        }
        for(let i=1;i<=range.Rows.Count;i++)
        {
            doMergeContent(range.Rows(i), false, separator, find_values)
        }
    }
    else
    {
        if (range.Columns.Count > 500)
        {
            if (MsgBox("您选择的区域比较大，合并单元格可能需要耗时几分钟、甚至更久。\\n是否继续？",jsOKCancel) != 1)
                return
        }
        for(let i=1 ; i<=range.Columns.Count;i++)
        {
            doMergeContent(range.Columns(i), false, separator, find_values)
        }
    }
}
"""

}