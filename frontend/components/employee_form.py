import dash_bootstrap_components as dbc
from dash import html, dcc


def employee_form(employee_id=None):
    """
    员工表单

    :param employee_id: 编辑时传入员工 Redmine Issue ID，新增时为空
    """
    return dbc.Form(
        [
            # 隐藏字段：编辑时使用
            dcc.Input(id="emp-id", value=employee_id, style={"display": "none"}) if employee_id else
            dcc.Input(id="emp-id", style={"display": "none"}),

            dbc.Row([
                dbc.Col(dbc.Label("人员编号", className="fw-bold"), width=3),
                dbc.Col(dbc.Input(id="emp-number", placeholder="人员编号"), width=9),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col(dbc.Label("姓名", className="fw-bold"), width=3),
                dbc.Col(dbc.Input(id="emp-name", placeholder="姓名"), width=9),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col(dbc.Label("性别", className="fw-bold"), width=3),
                dbc.Col(dbc.Input(id="emp-gender", placeholder="男/女"), width=9),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col(dbc.Label("年龄", className="fw-bold"), width=3),
                dbc.Col(dbc.Input(id="emp-age", placeholder="年龄", type="number"), width=9),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col(dbc.Label("手机号", className="fw-bold"), width=3),
                dbc.Col(dbc.Input(id="emp-phone", placeholder="手机号"), width=9),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col(dbc.Label("邮箱", className="fw-bold"), width=3),
                dbc.Col(dbc.Input(id="emp-email", placeholder="邮箱", type="email"), width=9),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col(dbc.Label("部门", className="fw-bold"), width=3),
                dbc.Col(dbc.Input(id="emp-department", placeholder="部门"), width=9),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col(dbc.Label("职位", className="fw-bold"), width=3),
                dbc.Col(dbc.Input(id="emp-position", placeholder="职位"), width=9),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col(dbc.Label("入职时间", className="fw-bold"), width=3),
                dbc.Col(dbc.Input(id="emp-jointime", placeholder="YYYY-MM-DD", type="date"), width=9),
            ], className="mb-3"),

            # 更新时间由系统自动生成，不在表单中显示
        ]
    )
