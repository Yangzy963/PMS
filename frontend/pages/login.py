import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", title="登录")

layout = dbc.Container(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H3("用户登录", className="text-center mb-4"),

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
                                className="w-100"  # 按钮占满一行
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