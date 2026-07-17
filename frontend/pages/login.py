import dash
from dash import html, callback, Input, Output, State
import dash_bootstrap_components as dbc

from services import api_client

dash.register_page(__name__, path="/", title="登录")

layout = dbc.Container(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H3("用户登录", className="text-center mb-4"),

                    # 错误提示
                    html.Div(id="login-error", className="text-danger text-center mb-3"),

                    # 垂直布局
                    dbc.Form(
                        [
                            dbc.Label("用户名", className="mb-1"),
                            dbc.Input(
                                placeholder="请输入用户名",
                                id="username",
                                type="text",
                                className="mb-3"
                            ),

                            dbc.Label("密码", className="mb-1"),
                            dbc.Input(
                                placeholder="请输入密码",
                                id="password",
                                type="password",
                                className="mb-3"
                            ),

                            dbc.Button(
                                "登录",
                                color="primary",
                                id="login-button",
                                className="w-100"
                            ),
                        ]
                    ),
                ]
            ),
            style={
                "width": "420px",
                "margin": "120px auto",
                "padding": "30px"
            },
        )
    ],
    fluid=True,
)


@callback(
    [Output("auth-store", "data", allow_duplicate=True),
     Output("url", "pathname", allow_duplicate=True),
     Output("login-error", "children")],
    Input("login-button", "n_clicks"),
    [State("username", "value"),
     State("password", "value")],
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    """处理登录"""
    if not n_clicks:
        return dash.no_update, dash.no_update, ""

    if not username or not password:
        return dash.no_update, dash.no_update, "请输入用户名和密码"

    result = api_client.login(username, password)

    if result.get("code") == 200:
        token = result["data"]["access_token"]
        return {"token": token}, "/employee", ""

    return dash.no_update, dash.no_update, result.get("message", "登录失败，请检查用户名和密码")
