import base64
import io
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

        # 搜索条件
        dcc.Store(id="search-params", data={}),

        # 排序状态
        dcc.Store(id="sort-state", data={"field": "", "direction": "asc"}),

        # 刷新触发器
        dcc.Store(id="refresh-trigger", data=0),

        # 当前待删除的人员 ID
        dcc.Store(id="delete-employee-id", data=None),

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

        # 操作结果提示（删除成功/失败等），显示在表格上方
        html.Div(id="batch-delete-result"),

        # 消息定时清除器
        dcc.Interval(id="message-timer", interval=5000),

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

        # 删除确认弹窗
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("确认删除")),
                dbc.ModalBody("确定要删除该人员吗？此操作不可恢复。"),
                dbc.ModalFooter([
                    dbc.Button("确定删除", id="confirm-single-delete", color="danger"),
                    dbc.Button("取消", id="cancel-single-delete", color="secondary"),
                ]),
            ],
            id="delete-confirm-modal",
            is_open=False,
        ),

        # 隐藏占位元素，用于满足旧 callback 输出
        html.Div(id="dummy-output", style={"display": "none"}),
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
     Input("employee-pagination", "active_page"),
     Input("search-params", "data"),
     Input("sort-state", "data")],
    State("auth-store", "data"),
)
def load_employees(pathname, refresh, active_page, search_params, sort_state, auth_data):
    """从后端加载人员列表（支持分页、搜索和排序）"""
    if pathname != "/employee":
        return dash.no_update, dash.no_update, dash.no_update

    token = auth_data.get("token") if auth_data else None
    if not token:
        # 无 Token 时不请求，由路由守卫处理跳转
        return [], dash.no_update, {"page": 1, "total": 0}

    page = active_page or 1
    limit = 20
    offset = (page - 1) * limit

    params = {"offset": offset, "limit": limit}

    # 添加排序条件
    sort_field = sort_state.get("field") if sort_state else ""
    if sort_field:
        params["sort"] = f"{sort_field}:{sort_state.get('direction', 'asc')}"

    # 添加搜索条件
    if search_params:
        if search_params.get("name"):
            params["name"] = search_params["name"]
        if search_params.get("department"):
            params["department"] = search_params["department"]
        if search_params.get("position"):
            params["position"] = search_params["position"]
        if search_params.get("jointime_start"):
            params["jointime_start"] = search_params["jointime_start"]
        if search_params.get("jointime_end"):
            params["jointime_end"] = search_params["jointime_end"]

    try:
        result = api_client.get_employees(token, params=params)
        if result.get("code") == 200:
            data = result.get("data", {})
            items = data.get("items", [])
            total = data.get("total", 0)
            return items, "", {"page": page, "total": total}
        else:
            return [], dbc.Alert(f"加载失败：{result.get('message')}", color="danger", className="mt-3"), {"page": 1, "total": 0}
    except Exception as e:
        return [], dbc.Alert(f"请求异常：{str(e)}", color="danger", className="mt-3"), {"page": 1, "total": 0}


# ====================== 排序 ======================
@callback(
    Output("sort-state", "data"),
    Input({"type": "sort-header", "index": ALL}, "n_clicks"),
    State("sort-state", "data"),
    prevent_initial_call=True
)
def handle_sort(clicks_list, sort_state):
    """点击表头排序"""
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update

    clicked = ctx.triggered[0]["prop_id"]
    # 从 prop_id 解析字段名，格式为 {"type":"sort-header","index":"number"}.n_clicks
    import json
    try:
        field = json.loads(clicked.split(".n_clicks")[0])["index"]
    except Exception:
        return dash.no_update

    current_field = sort_state.get("field", "")
    current_dir = sort_state.get("direction", "asc")

    if field == current_field:
        # 同字段切换方向
        return {"field": field, "direction": "desc" if current_dir == "asc" else "asc"}
    else:
        # 不同字段默认升序
        return {"field": field, "direction": "asc"}


# ====================== 搜索与重置 ======================
@callback(
    [Output("search-params", "data"),
     Output("employee-pagination", "active_page", allow_duplicate=True)],
    Input("search-btn", "n_clicks"),
    [State("name-search", "value"),
     State("department-search", "value"),
     State("position-search", "value"),
     State("jointime-range", "start_date"),
     State("jointime-range", "end_date")],
    prevent_initial_call=True
)
def handle_search(n_clicks, name, department, position, start_date, end_date):
    """点击查询按钮时更新搜索条件并重置到第一页"""
    if not n_clicks:
        return dash.no_update, dash.no_update

    params = {}
    if name:
        params["name"] = name
    if department:
        params["department"] = department
    if position:
        params["position"] = position
    if start_date:
        params["jointime_start"] = start_date
    if end_date:
        params["jointime_end"] = end_date

    return params, 1


@callback(
    [Output("search-params", "data", allow_duplicate=True),
     Output("name-search", "value"),
     Output("department-search", "value"),
     Output("position-search", "value"),
     Output("jointime-range", "start_date"),
     Output("jointime-range", "end_date"),
     Output("employee-pagination", "active_page", allow_duplicate=True)],
    Input("reset-btn", "n_clicks"),
    prevent_initial_call=True
)
def handle_reset(n_clicks):
    """点击重置按钮时清空搜索条件并重置到第一页"""
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    return {}, None, None, None, None, None, 1


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
     Input("batch-mode", "data"),
     Input("sort-state", "data")]
)
def render_employee_table(employees_data, batch_mode, sort_state):
    """根据批量模式和排序状态重新渲染表格"""
    return employee_table(
        employees_data or [],
        selection_mode=batch_mode,
        sort_field=sort_state.get("field", ""),
        sort_direction=sort_state.get("direction", "asc"),
    )


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


# ====================== 消息自动清除 ======================
@callback(
    Output("batch-delete-result", "children", allow_duplicate=True),
    Input("message-timer", "n_intervals"),
    State("batch-delete-result", "children"),
    prevent_initial_call=True,
)
def auto_clear_message(n_intervals, current_message):
    """操作提示 5 秒后自动消失"""
    if current_message:
        return ""
    return dash.no_update


# ====================== 单条删除：打开确认弹窗 ======================
@callback(
    [Output("delete-confirm-modal", "is_open"),
     Output("delete-employee-id", "data")],
    Input({"type": "delete-button", "index": ALL}, "n_clicks"),
    State("employees-data", "data"),
    prevent_initial_call=True
)
def open_delete_modal(delete_clicks, employees_data):
    """点击单条删除按钮时打开确认弹窗"""
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update

    for i, n in enumerate(delete_clicks or []):
        if n:
            emp = employees_data[i] if i < len(employees_data) else {}
            return True, emp.get("id")

    return dash.no_update, dash.no_update


# ====================== 单条删除：确认删除 ======================
@callback(
    [Output("delete-confirm-modal", "is_open", allow_duplicate=True),
     Output("refresh-trigger", "data", allow_duplicate=True),
     Output("batch-delete-result", "children")],
    Input("confirm-single-delete", "n_clicks"),
    [State("delete-employee-id", "data"),
     State("auth-store", "data"),
     State("refresh-trigger", "data")],
    prevent_initial_call=True
)
def confirm_single_delete(n_clicks, employee_id, auth_data, refresh_data):
    """确认单条删除"""
    if not n_clicks or not employee_id:
        return dash.no_update, dash.no_update, dash.no_update

    token = auth_data.get("token") if auth_data else None
    if not token:
        return False, dash.no_update, dbc.Alert("登录已过期", color="warning", className="mt-3")

    try:
        result = api_client.delete_employee(token, employee_id)
        if result.get("code") == 200:
            return False, (refresh_data or 0) + 1, dbc.Alert("删除人员成功", color="success", className="mt-3")
        else:
            return False, dash.no_update, dbc.Alert(f"删除失败：{result.get('message')}", color="danger", className="mt-3")
    except Exception as e:
        return False, dash.no_update, dbc.Alert(f"请求异常：{str(e)}", color="danger", className="mt-3")


# ====================== 单条删除：取消删除 ======================
@callback(
    Output("delete-confirm-modal", "is_open", allow_duplicate=True),
    Input("cancel-single-delete", "n_clicks"),
    prevent_initial_call=True
)
def cancel_single_delete(n_clicks):
    """取消单条删除"""
    if n_clicks:
        return False
    return dash.no_update


# ====================== 确认批量删除 ======================
@callback(
    [Output("batch-delete-result", "children", allow_duplicate=True),
     Output("refresh-trigger", "data", allow_duplicate=True),
     Output("batch-mode", "data", allow_duplicate=True)],
    Input("confirm-batch-delete", "n_clicks"),
    [State({"type": "select-checkbox", "index": ALL}, "value"),
     State("employees-data", "data"),
     State("auth-store", "data"),
     State("refresh-trigger", "data")],
    prevent_initial_call=True
)
def confirm_batch_delete(n_clicks, selected_values, employees_data, auth_data, refresh_data):
    """处理批量删除确认"""
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update

    selected_indices = [i for i, v in enumerate(selected_values) if v]

    if not selected_indices:
        return dbc.Alert("请先选择要删除的人员", color="warning", className="mt-3"), dash.no_update, dash.no_update

    token = auth_data.get("token") if auth_data else None
    if not token:
        return dbc.Alert("登录已过期", color="warning", className="mt-3"), dash.no_update, False

    # 获取选中人员的 Redmine Issue ID
    employee_ids = []
    for idx in selected_indices:
        if idx < len(employees_data):
            emp_id = employees_data[idx].get("id")
            if emp_id:
                employee_ids.append(emp_id)

    if not employee_ids:
        return dbc.Alert("未获取到有效的员工 ID", color="warning", className="mt-3"), dash.no_update, dash.no_update

    try:
        result = api_client.batch_delete_employees(token, employee_ids)
        if result.get("code") == 200:
            deleted_count = result.get("data", {}).get("deleted_count", 0)
            return (
                dbc.Alert(f"成功删除 {deleted_count} 条人员记录", color="success", className="mt-3"),
                (refresh_data or 0) + 1,
                False
            )
        else:
            return dbc.Alert(f"批量删除失败：{result.get('message')}", color="danger", className="mt-3"), dash.no_update, dash.no_update
    except Exception as e:
        return dbc.Alert(f"请求异常：{str(e)}", color="danger", className="mt-3"), dash.no_update, dash.no_update


# ====================== 统一控制 Modal 的 Callback ======================
@callback(
    [Output("employee-modal", "is_open"),
     Output("modal-title", "children"),
     Output("emp-id", "value"),
     Output("emp-number", "value"),
     Output("emp-name", "value"),
     Output("emp-gender", "value"),
     Output("emp-age", "value"),
     Output("emp-phone", "value"),
     Output("emp-email", "value"),
     Output("emp-department", "value"),
     Output("emp-position", "value"),
     Output("emp-jointime", "value")],
    [
        Input("open-modal", "n_clicks"),
        Input({"type": "edit-button", "index": ALL}, "n_clicks"),
        Input("close-modal", "n_clicks"),
    ],
    [State("employee-modal", "is_open"),
     State("employees-data", "data")],
    prevent_initial_call=True
)
def handle_modal(open_click, edit_clicks, close_click, is_open, employees_data):
    ctx = callback_context
    if not ctx.triggered:
        return [dash.no_update] * 12

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # 空表单值
    empty_form = ["", "", "", None, "", "", "", "", ""]

    # 只有按钮确实被点击过才打开弹窗，避免组件重建时误触发
    if trigger_id == "open-modal" and open_click:
        return [True, "新增人员", ""] + empty_form

    elif "edit-button" in trigger_id:
        for i, n in enumerate(edit_clicks or []):
            if n:
                emp = employees_data[i] if i < len(employees_data) else {}
                return [
                    True,
                    "编辑人员",
                    emp.get("id"),
                    emp.get("number", ""),
                    emp.get("name", ""),
                    emp.get("gender", ""),
                    emp.get("age"),
                    emp.get("phone", ""),
                    emp.get("email", ""),
                    emp.get("department", ""),
                    emp.get("position", ""),
                    emp.get("jointime", ""),
                ]

    elif trigger_id == "close-modal":
        return [False, dash.no_update, ""] + empty_form

    return [is_open, dash.no_update, dash.no_update] + [dash.no_update] * 9


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


# 保存人员信息（新增/编辑）
@callback(
    [Output("employee-modal", "is_open", allow_duplicate=True),
     Output("refresh-trigger", "data", allow_duplicate=True),
     Output("save-result", "children"),
     Output("emp-number", "value", allow_duplicate=True),
     Output("emp-name", "value", allow_duplicate=True),
     Output("emp-gender", "value", allow_duplicate=True),
     Output("emp-age", "value", allow_duplicate=True),
     Output("emp-phone", "value", allow_duplicate=True),
     Output("emp-email", "value", allow_duplicate=True),
     Output("emp-department", "value", allow_duplicate=True),
     Output("emp-position", "value", allow_duplicate=True),
     Output("emp-jointime", "value", allow_duplicate=True)],
    Input("save-employee", "n_clicks"),
    [State("emp-id", "value"),
     State("emp-number", "value"),
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
def save_employee(n_clicks, emp_id, number, name, gender, age, phone, email, department, position, jointime, auth_data, refresh_data):
    """新增或编辑人员"""
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
        if emp_id:
            # 编辑
            result = api_client.update_employee(token, emp_id, data)
            action = "编辑"
        else:
            # 新增
            result = api_client.create_employee(token, data)
            action = "新增"

        if result.get("code") == 200:
            # 保存成功：关闭弹窗、刷新列表、清空表单
            return False, (refresh_data or 0) + 1, dbc.Alert(f"{action}人员成功", color="success"), "", "", "", None, "", "", "", "", ""
        else:
            return dash.no_update, dash.no_update, dbc.Alert(f"{action}失败：{result.get('message')}", color="danger"), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    except Exception as e:
        return dash.no_update, dash.no_update, dbc.Alert(f"请求异常：{str(e)}", color="danger"), dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


# ====================== 数据导入 ======================
@callback(
    [Output("batch-delete-result", "children", allow_duplicate=True),
     Output("refresh-trigger", "data", allow_duplicate=True)],
    Input("upload-employee-data", "contents"),
    [State("upload-employee-data", "filename"),
     State("auth-store", "data"),
     State("refresh-trigger", "data")],
    prevent_initial_call=True
)
def handle_import(contents, filename, auth_data, refresh_data):
    """处理数据导入"""
    if not contents or not filename:
        return dash.no_update, dash.no_update

    token = auth_data.get("token") if auth_data else None
    if not token:
        return dbc.Alert("登录已过期，请重新登录", color="warning", className="mt-3"), dash.no_update

    # 解析 base64 编码的文件内容
    _, content_string = contents.split(",")
    file_bytes = base64.b64decode(content_string)

    try:
        import_result = api_client.import_employees(
            token,
            files={"file": (filename, io.BytesIO(file_bytes))},
        )

        if import_result.get("code") == 200:
            data = import_result.get("data", {})
            total = data.get("total", 0)
            success = data.get("success", 0)
            failed = data.get("failed", 0)
            skipped = data.get("skipped", 0)
            overwritten = data.get("overwritten", 0)

            parts = [f"导入完成：共 {total} 条"]
            if success:
                parts.append(f"成功 {success} 条")
            if overwritten:
                parts.append(f"覆盖 {overwritten} 条")
            if skipped:
                parts.append(f"跳过 {skipped} 条")
            if failed:
                parts.append(f"失败 {failed} 条")

            message = "，".join(parts)
            color = "success" if failed == 0 else "warning"
            return dbc.Alert(message, color=color, className="mt-3"), (refresh_data or 0) + 1
        else:
            return dbc.Alert(f"导入失败：{import_result.get('message')}", color="danger", className="mt-3"), dash.no_update
    except Exception as e:
        return dbc.Alert(f"导入异常：{str(e)}", color="danger", className="mt-3"), dash.no_update
