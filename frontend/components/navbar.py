import dash_bootstrap_components as dbc
from dash import html


def navbar(is_logged_in=False):
    """
    导航栏

    :param is_logged_in: 是否已登录
    """
    nav_items = []

    if is_logged_in:
        # 登录后显示：人员管理、退出登录
        nav_items.append(dbc.NavLink("人员管理", href="/employee", active="exact"))
        nav_items.append(
            # 退出登录按钮：调用后端登出接口使 Token 失效，跳转回登录页
            dbc.Button(
                "退出登录",
                id="logout-button",
                color="light",
                size="sm",
                className="ms-2"
            ),
        )
    else:
        # 未登录时只显示：首页（登录页）
        nav_items.append(dbc.NavLink("首页", href="/", active="exact"))

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

                # 右侧导航链接
                dbc.Nav(
                    nav_items,
                    className="ms-auto",  # 靠右
                ),
            ],
            fluid=True,
        ),
        color="primary",
        dark=True,
    )
