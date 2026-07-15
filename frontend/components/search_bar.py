from dash import html, dcc
import dash_bootstrap_components as dbc


def search_bar():
    return dbc.Row(
        [
            dbc.Col(
                dcc.Input(
                    id="name-search",
                    placeholder="姓名模糊搜索",
                    className="mb-2"
                ),
                width=3
            ),

            dbc.Col(
                dcc.Dropdown(
                    id="department-search",
                    options=[
                        {"label": "全部", "value": "all"},
                        {"label": "研发部", "value": "研发部"},
                        {"label": "测试部", "value": "测试部"},
                        {"label": "销售部", "value": "销售部"},
                    ],
                    placeholder="选择部门",
                    className="mb-2"
                ),
                width=2
            ),

            dbc.Col(
                dcc.Dropdown(
                    id="position-search",
                    options=[
                        {"label": "全部", "value": "all"},
                        {"label": "Python工程师", "value": "Python工程师"},
                        {"label": "测试工程师", "value": "测试工程师"},
                        {"label": "销售专员", "value": "销售专员"},
                    ],
                    placeholder="选择职位",
                    className="mb-2"
                ),
                width=2
            ),

            dbc.Col(
                dbc.Row([
                    dbc.Col(
                        dcc.DatePickerRange(
                            id="jointime-range",
                            start_date_placeholder_text="入职开始",
                            end_date_placeholder_text="入职结束",
                            className="mb-2"
                        ),
                        width=8
                    ),
                ]),
                width=3
            ),

            dbc.Col(
                dbc.Button(
                    "查询",
                    id="search-btn",
                    color="primary",
                    className="mb-2"
                ),
                width=1
            ),

            dbc.Col(
                dbc.Button(
                    "重置",
                    id="reset-btn",
                    color="secondary",
                    className="mb-2"
                ),
                width=1
            ),
        ],
        className="mb-3 align-items-end"
    )