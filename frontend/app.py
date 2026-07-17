from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import dash

from components.navbar import navbar


app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)


app.layout = dbc.Container(
    [

        dcc.Location(
            id="url"
        ),

        # 登录状态存储（local 可在同一浏览器多个标签页共享）
        dcc.Store(id="auth-store", storage_type="local"),


        # 导航栏（动态渲染）
        html.Div(id="navbar-container"),


        # 页面内容
        dash.page_container

    ],

    fluid=True

)


@app.callback(
    Output("navbar-container", "children"),
    Input("auth-store", "data"),
)
def render_navbar(auth_data):
    """根据登录状态渲染导航栏"""
    is_logged_in = bool(auth_data and auth_data.get("token"))
    return navbar(is_logged_in=is_logged_in)


@app.callback(
    [Output("auth-store", "data", allow_duplicate=True),
     Output("url", "pathname", allow_duplicate=True)],
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    """退出登录：清除 Token 并返回登录页"""
    if n_clicks:
        return None, "/"
    return dash.no_update, dash.no_update


@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("url", "pathname"),
    State("auth-store", "data"),
    prevent_initial_call=True
)
def route_guard(pathname, auth_data):
    """路由权限控制：未登录时只能访问首页"""
    is_logged_in = bool(auth_data and auth_data.get("token"))

    # 未登录且访问非首页页面，重定向到登录页
    if not is_logged_in and pathname != "/":
        return "/"

    return dash.no_update


if __name__ == "__main__":

    app.run(debug=True)
