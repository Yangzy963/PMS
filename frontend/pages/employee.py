import dash
from dash import html, dcc, callback, Input, Output, State, ALL, callback_context
import dash_bootstrap_components as dbc

from components.employee_table import employee_table
from components.search_bar import search_bar
from components.employee_form import employee_form
from services import api_client

dash.register_page(__name__, path="/employee", title="人员管理")

# ====================== Modal ======================
employee_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle(id="modal-title")),
        dbc.ModalBody([
            employee_form(),
            html.Div(id="save-result", className="mt-3"),
        ]),
        dbc.ModalFooter([
            dbc.Button("保存", id="save-employee", color="success"),
            dbc.Button("取消", id="close-modal", color="secondary"),
        ]),
    ],
    id="employee-modal",
    is_open=False,
    size="lg",
)

layout = dbc.Container(
    [
        html.H2("人员信息管理", className="mb-3"),

        # 批量删除模式状态
        dcc.Store(id="batch-mode", data=False),

        # 人员数据缓存
        dcc.Store(id="employees-data", data=[]),

        # 分页信息
        dcc.Store(id="pagination-info", data={"page": 1, "total": 0}),

        # 刷新触发器
        dcc.Store(id="refresh-trigger", data=0),

        # 顶部操作按钮行
        dbc.Row([
            dbc.Col(dbc.Button("新增人员", id="open-modal", color="success"), width="auto"),

            # 批量删除按钮（普通模式显示）
            dbc.Col(
                dbc.Button("批量删除", id="batch-delete", color="danger"),
                width="auto",
                id="batch-delete-col"
            ),

            # 确认删除按钮（批量模式显示）
            dbc.Col(
                dbc.Button("确认删除", id="confirm-batch-delete", color="danger"),
                width="auto",
                id="confirm-batch-delete-col",
                style={"display": "none"}
            ),

            # 取消按钮（批量模式显示）
            dbc.Col(
                dbc.Button("取消", id="cancel-batch-delete", color="secondary"),
                width="auto",
                id="cancel-batch-delete-col",
                style={"display": "none"}
            ),

            # 数据导入（普通模式显示）
            dbc.Col(
                html.Div(
                    dcc.Upload(
                        id="upload-employee-data",
                        children=dbc.Button("数据导入", color="primary"),
                        multiple=False,
                    ),
                    id="import-col"
                ),
                width="auto"
            ),
        ], className="mb-3"),

        search_bar(),
        html.Hr(),

        # 状态提示（加载中、错误等）
        html.Div(id="employee-list-status"),

        # 动态表格容器
        html.Div(id="employee-table-container"),

        # 分页信息
        html.Div(id="pagination-info-display", className="text-muted mt-2"),

        # 分页控件
        dbc.Pagination(
            id="employee-pagination",
            active_page=1,
            max_value=1,
            fully_expanded=False,
            className="mt-3"
        ),

        employee_modal,

        # 隐藏占位元素，用于满足旧 callback 输出
        html.Div(id="dummy-output", style={"display": "none"}),

        # 批量删除结果提示
        html.Div(id="batch-delete-result"),
    ],
    fluid=True
)


# ====================== 加载人员列表数据 ======================
@callback(
    [Output("employees-data", "data"),
     Output("employee-list-status", "children"),
     Output("pagination-info", "data")],
    [Input("url", "pathname"),
     Input("refresh-trigger", "data"),
     Input("employee-pagination", "active_page")],
    State("auth-store", "data"),
)
def load_employees(pathname, refresh, active_page, auth_data):
    """从后端加载人员列表（支持分页）"""
    if pathname != "/employee":
        return dash.no_update, dash.no_update, dash.no_update

    token = auth_data.get("token") if auth_data else None
    if not token:
        # 无 Token 时不请求，由路由守卫处理跳转
        return [], dash.no_update, {"page": 1, "total": 0}

    page = active_page or 1
    limit = 20
    offset = (page - 1) * limit

    try:
        result = api_client.get_employees(token, params={"offset": offset, "limit": limit})
        if result.get("code") == 200:
            data = result.get("data", {})
            items = data.get("items", [])
            total = data.get("total", 0)
            return items, "", {"page": page, "total": total}
        else:
            return [], dbc.Alert(f"加载失败：{result.get('message')}", color="danger", className="mt-3"), {"page": 1, "total": 0}
    except Exception as e:
        return [], dbc.Alert(f"请求异常：{str(e)}", color="danger", className="mt-3"), {"page": 1, "total": 0}


# ====================== 分页控件更新 ======================
@callback(
    [Output("employee-pagination", "max_value"),
     Output("pagination-info-display", "children")],
    Input("pagination-info", "data"),
)
def update_pagination(pagination_info):
    """根据总数更新分页控件"""
    total = pagination_info.get("total", 0)
    page = pagination_info.get("page", 1)
    limit = 20
    max_page = max(1, (total + limit - 1) // limit)

    info = f"共 {total} 条记录，当前第 {page} 页，每页 {limit} 条"
    return max_page, info


# ====================== 切换页面时重置到第一页 ======================
@callback(
    Output("employee-pagination", "active_page"),
    Input("url", "pathname"),
    prevent_initial_call=True
)
def reset_pagination(pathname):
    """进入人员管理页时重置到第一页"""
    if pathname == "/employee":
        return 1
    return dash.no_update


# ====================== 表格渲染（根据批量模式动态显示勾选框）======================
@callback(
    Output("employee-table-container", "children"),
    [Input("employees-data", "data"),
     Input("batch-mode", "data")]
)
def render_employee_table(employees_data, batch_mode):
    """根据批量模式重新渲染表格"""
    return employee_table(employees_data or [], selection_mode=batch_mode)


# ====================== 批量删除模式切换 ======================
@callback(
    [Output("batch-mode", "data"),
     Output("batch-delete-col", "style"),
     Output("confirm-batch-delete-col", "style"),
     Output("cancel-batch-delete-col", "style"),
     Output("import-col", "style")],
    [Input("batch-delete", "n_clicks"),
     Input("cancel-batch-delete", "n_clicks"),
     Input("confirm-batch-delete", "n_clicks")],
    State("batch-mode", "data"),
    prevent_initial_call=True
)
def toggle_batch_mode(batch_click, cancel_click, confirm_click, batch_mode):
    """切换批量删除模式"""
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "batch-delete":
        # 进入批量模式
        return True, {"display": "none"}, {"display": "block"}, {"display": "block"}, {"display": "none"}

    # 取消或确认都退出批量模式
    return False, {"display": "block"}, {"display": "none"}, {"display": "none"}, {"display": "block"}


# ====================== 确认批量删除 ======================
@callback(
    Output("batch-delete-result", "children"),
    Input("confirm-batch-delete", "n_clicks"),
    State({"type": "select-checkbox", "index": ALL}, "value"),
    prevent_initial_call=True
)
def confirm_batch_delete(n_clicks, selected_values):
    """处理批量删除确认"""
    if not n_clicks:
        return dash.no_update

    selected_indices = [i for i, v in enumerate(selected_values) if v]

    if not selected_indices:
        return dbc.Alert("请先选择要删除的人员", color="warning", className="mt-3")

    # TODO: 后续接入 Redmine API 执行真实删除
    print(f"🗑️ 批量删除选中的人员索引: {selected_indices}")

    return dbc.Alert(
        f"已选择 {len(selected_indices)} 条记录进行批量删除（当前为 Mock，后续对接 Redmine）",
        color="info",
        className="mt-3"
    )


# ====================== 统一控制 Modal 的 Callback ======================
@callback(
    [Output("employee-modal", "is_open"),
     Output("modal-title", "children")],
    [
        Input("open-modal", "n_clicks"),
        Input({"type": "edit-button", "index": ALL}, "n_clicks"),
        Input("close-modal", "n_clicks"),
    ],
    State("employee-modal", "is_open"),
    prevent_initial_call=True
)
def handle_modal(open_click, edit_clicks, close_click, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # 只有按钮确实被点击过才打开弹窗，避免组件重建时误触发
    if trigger_id == "open-modal" and open_click:
        return True, "新增人员"

    elif "edit-button" in trigger_id:
        if any(n for n in (edit_clicks or []) if n):
            return True, "编辑人员"

    elif trigger_id == "close-modal":
        return False, dash.no_update

    return is_open, dash.no_update


# ====================== 弹窗打开/关闭时清空保存结果提示 ======================
@callback(
    Output("save-result", "children", allow_duplicate=True),
    Input("employee-modal", "is_open"),
    prevent_initial_call=True
)
def clear_save_result(is_open):
    """弹窗状态变化时清空保存结果提示"""
    if is_open:
        return ""
    return dash.no_update


# 保存人员信息（新增）
@callback(
    [Output("employee-modal", "is_open", allow_duplicate=True),
     Output("refresh-trigger", "data", allow_duplicate=True),
     Output("save-result", "children"),
     Output("emp-number", "value"),
     Output("emp-name", "value"),
     Output("emp-gender", "value"),
     Output("emp-age", "value"),
     Output("emp-phone", "value"),
     Output("emp-email", "value"),
     Output("emp-department", "value"),
     Output("emp-position", "value"),
     Output("emp-jointime", "value")],
    Input("save-employee", "n_clicks"),
    [State("emp-number", "value"),
     State("emp-name", "value"),
     State("emp-gender", "value"),
     State("emp-age", "value"),
     State("emp-phone", "value"),
     State("emp-email", "value"),
     State("emp-department", "value"),
     State("emp-position", "value"),
     State("emp-jointime", "value"),
     State("auth-store", "data"),
     State("refresh-trigger", "data")],
    prevent_initial_call=True
)
def save_employee(n_clicks, number, name, gender, age, phone, email, department, position, jointime, auth_data, refresh_data):
    """新增人员"""
    if not n_clicks:
        return dash.no_update, dash.no_update, "", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # 校验必填字段
    if not number or not name:
        return dash.no_update, dash.no_update, dbc.Alert("人员编号和姓名不能为空", color="danger"), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    token = auth_data.get("token") if auth_data else None
    if not token:
        return dash.no_update, dash.no_update, dbc.Alert("登录已过期，请重新登录", color="warning"), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    data = {
        "number": number,
        "name": name,
        "gender": gender or "",
        "age": int(age) if age else None,
        "phone": phone or "",
        "email": email or "",
        "department": department or "",
        "position": position or "",
        "jointime": jointime or "",
    }

    try:
        result = api_client.create_employee(token, data)
        if result.get("code") == 200:
            # 新增成功：关闭弹窗、刷新列表、清空表单
            return False, (refresh_data or 0) + 1, dbc.Alert("新增人员成功", color="success"), "", "", "", None, "", "", "", "", ""
        else:
            return dash.no_update, dash.no_update, dbc.Alert(f"新增失败：{result.get('message')}", color="danger"), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    except Exception as e:
        return dash.no_update, dash.no_update, dbc.Alert(f"请求异常：{str(e)}", color="danger"), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
