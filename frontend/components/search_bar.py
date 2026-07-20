from dash import html, dcc
import dash_bootstrap_components as dbc


def search_bar():
    return dbc.Row(
        [
            dbc.Col(
                dbc.Input(
                    id="name-search",
                    placeholder="姓名模糊搜索",
                    className="mb-2"
                ),
                xs=12, sm=6, md=3, lg=2
            ),

            dbc.Col(
                dbc.Input(
                    id="department-search",
                    placeholder="部门",
                    className="mb-2"
                ),
                xs=12, sm=6, md=3, lg=2
            ),

            dbc.Col(
                dbc.Input(
                    id="position-search",
                    placeholder="职位",
                    className="mb-2"
                ),
                xs=12, sm=6, md=3, lg=2
            ),

            dbc.Col(
                dcc.DatePickerRange(
                    id="jointime-range",
                    start_date_placeholder_text="入职开始",
                    end_date_placeholder_text="入职结束",
                    className="mb-2",
                    style={"width": "100%"}
                ),
                xs=12, sm=6, md=3, lg=3
            ),

            dbc.Col(
                # 查询按钮：根据当前搜索条件刷新人员列表，重置到第一页
                dbc.Button(
                    "查询",
                    id="search-btn",
                    color="primary",
                    className="mb-2"
                ),
                xs=6, sm=3, md=1, lg=1
            ),

            dbc.Col(
                # 重置按钮：清空所有搜索条件并恢复到第一页
                dbc.Button(
                    "重置",
                    id="reset-btn",
                    color="secondary",
                    className="mb-2"
                ),
                xs=6, sm=3, md=1, lg=1
            ),
        ],
        className="mb-3 align-items-end"
    )
