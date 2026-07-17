import dash
from dash import html, dcc, callback, Input, Output, State, ALL, callback_context
import dash_bootstrap_components as dbc

from components.employee_table import employee_table
from components.search_bar import search_bar
from components.employee_form import employee_form
from data.mock_employee import employees

dash.register_page(__name__, path="/employee", title="人员管理")

# ====================== Modal ======================
employee_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle(id="modal-title")),
        dbc.ModalBody(employee_form()),
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

        # 动态表格容器
        html.Div(id="employee-table-container"),

        employee_modal,

        # 隐藏占位元素，用于满足旧 callback 输出
        html.Div(id="dummy-output", style={"display": "none"}),

        # 批量删除结果提示
        html.Div(id="batch-delete-result"),
    ],
    fluid=True
)


# ====================== 表格渲染（根据批量模式动态显示勾选框）======================
@callback(
    Output("employee-table-container", "children"),
    Input("batch-mode", "data")
)
def render_employee_table(batch_mode):
    """根据批量模式重新渲染表格"""
    return employee_table(employees, selection_mode=batch_mode)


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
        Input("save-employee", "n_clicks")
    ],
    State("employee-modal", "is_open"),
    prevent_initial_call=True
)
def handle_modal(open_click, edit_clicks, close_click, save_click, is_open):
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

    elif trigger_id in ["close-modal", "save-employee"]:
        return False, dash.no_update

    return is_open, dash.no_update


# 保存成功后的提示（可后续扩展）
@callback(
    Output("dummy-output", "children", allow_duplicate=True),
    Input("save-employee", "n_clicks"),
    prevent_initial_call=True
)
def save_employee(n_clicks):
    if n_clicks:
        print("✅ 人员信息保存成功（Mock）")
    return ""
