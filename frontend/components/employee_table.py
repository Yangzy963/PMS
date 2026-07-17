import dash_bootstrap_components as dbc
from dash import html


def employee_table(data, selection_mode=False):
    """
    员工信息表格

    :param data: 员工数据列表，每项为 dict，需包含以下 key：
                 number, name, gender, age, phone, email, department, position,
                 jointime, createtime, updatetime
    :param selection_mode: 是否显示批量选择勾选框
    """
    # 基础表头
    base_headers = [
        "人员编号", "姓名", "性别", "年龄", "手机号", "邮箱",
        "部门", "职位", "入职时间", "创建时间", "更新时间", "操作"
    ]

    # 根据模式决定是否显示选择列
    if selection_mode:
        header_cells = [html.Th("选择")] + [html.Th(h) for h in base_headers]
    else:
        header_cells = [html.Th(h) for h in base_headers]

    header = html.Thead(html.Tr(header_cells))

    # 表格内容
    rows = []
    for i, emp in enumerate(data):
        # 操作按钮列（始终显示）
        action_cell = html.Td([
            dbc.Button("编辑", color="info", size="sm",
                       id={"type": "edit-button", "index": i}, className="me-1"),
            dbc.Button("删除", color="danger", size="sm",
                       id={"type": "delete-button", "index": i}),
        ])

        # 基础数据单元格
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
            row_cells = [
                html.Td(dbc.Checkbox(id={"type": "select-checkbox", "index": i}))
            ] + base_cells
        else:
            row_cells = base_cells

        rows.append(html.Tr(row_cells))

    body = html.Tbody(rows)

    return dbc.Table(
        [header, body],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True
    )
