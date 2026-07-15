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

        # 登录状态存储
        dcc.Store(id="auth-store", storage_type="session"),


        # 导航栏
        navbar(),


        # 页面内容
        dash.page_container

    ],

    fluid=True

)


@app.callback(
    [Output("auth-store", "data"),
     Output("url", "pathname")],
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    """退出登录：清除 Token 并返回登录页"""
    if n_clicks:
        return None, "/"
    return dash.no_update, dash.no_update


if __name__ == "__main__":

    app.run(debug=True)