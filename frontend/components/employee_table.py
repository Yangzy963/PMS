import dash_bootstrap_components as dbc
from dash import html


# 可排序的列：{表头文字: 字段名}
_SORTABLE_COLUMNS = {
    "人员编号": "number",
    "年龄": "age",
    "入职时间": "jointime",
}

# 基础表头顺序
_BASE_HEADERS = [
    "人员编号", "姓名", "性别", "年龄", "手机号", "邮箱",
    "部门", "职位", "入职时间", "创建时间", "更新时间", "操作",
]


def _build_header(text, sort_field, sort_direction):
    """构建表头单元格，可排序列始终显示三角箭头"""
    field = _SORTABLE_COLUMNS.get(text)

    # 不可排序的列
    if field is None:
        return html.Th(text)

    # 可排序列：始终显示箭头，当前排序列高亮，其余置灰
    is_active = field == sort_field
    if is_active:
        arrow = " ▲" if sort_direction == "asc" else " ▼"
        arrow_style = {"color": "#000"}
    else:
        arrow = " ▲"
        arrow_style = {"color": "#ccc"}

    return html.Th(
        html.Span([
            html.Span(text),
            html.Span(arrow, style=arrow_style),
        ],
            id={"type": "sort-header", "index": field},
            className="sortable-header",
            style={"cursor": "pointer", "userSelect": "none"}
        ),
    )


def employee_table(data, selection_mode=False, sort_field="", sort_direction="asc"):
    """
    员工信息表格

    :param data: 员工数据列表
    :param selection_mode: 是否显示批量选择勾选框
    :param sort_field: 当前排序字段
    :param sort_direction: 当前排序方向 "asc" / "desc"
    """
    # 表头
    header_cells = []
    if selection_mode:
        header_cells.append(html.Th("选择"))
    header_cells.extend(_build_header(h, sort_field, sort_direction) for h in _BASE_HEADERS)

    header = html.Thead(html.Tr(header_cells))

    # 表格内容
    rows = []
    for i, emp in enumerate(data):
        if selection_mode:
            action_cell = html.Td("-")
        else:
            action_cell = html.Td([
                # 编辑按钮：打开编辑弹窗，回填当前行数据
                dbc.Button("编辑", color="info", size="sm",
                           id={"type": "edit-button", "index": i}, className="me-1"),
                # 删除按钮：打开删除确认弹窗
                dbc.Button("删除", color="danger", size="sm",
                           id={"type": "delete-button", "index": i}),
            ])

        base_cells = [
            html.Td(emp.get("number", "")),
            html.Td(emp.get("name", "")),
            html.Td(emp.get("gender", "")),
            html.Td(emp.get("age", "")),
            html.Td(emp.get("phone", "")),
            html.Td(emp.get("email", "")),
            html.Td(emp.get("department", "")),
            html.Td(emp.get("position", "")),
            html.Td(emp.get("jointime", "")),
            html.Td(emp.get("createtime", "")),
            html.Td(emp.get("updatetime", "")),
            action_cell,
        ]

        if selection_mode:
            row_cells = [html.Td(dbc.Checkbox(id={"type": "select-checkbox", "index": i}))] + base_cells
        else:
            row_cells = base_cells

        rows.append(html.Tr(row_cells))

    body = html.Tbody(rows)

    return dbc.Table(
        [header, body],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
    )
