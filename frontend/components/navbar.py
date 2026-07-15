import dash_bootstrap_components as dbc
from dash import html


def navbar():
    return dbc.Navbar(
        dbc.Container(
            [
                # 使用 justify-content-center 让标题居中
                dbc.Row(
                    [
                        dbc.Col(
                            html.A(
                                "人员管理系统",
                                className="navbar-brand mx-auto text-center",
                                style={"fontSize": "1.5rem", "fontWeight": "bold"}
                            ),
                            width="auto"
                        ),
                    ],
                    className="w-100 justify-content-center"
                ),

                # 右侧导航链接 + 退出登录
                dbc.Nav(
                    [
                        dbc.NavLink("首页", href="/", active="exact"),
                        dbc.NavLink("人员管理", href="/employee", active="exact"),
                        dbc.Button(
                            "退出登录",
                            id="logout-button",
                            color="light",
                            size="sm",
                            className="ms-2"
                        ),
                    ],
                    className="ms-auto",  # 靠右
                ),
            ],
            fluid=True,
        ),
        color="primary",
        dark=True,
    )