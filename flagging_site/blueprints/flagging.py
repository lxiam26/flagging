import pandas as pd
from flask import Blueprint
from flask import render_template
from flagging_site.data.hobolink import get_hobolink_data
from flagging_site.data.usgs import get_usgs_data
from flagging_site.data.model import process_data
from flagging_site.data.model import reach_2_model
from flagging_site.data.model import reach_3_model
from flagging_site.data.model import reach_4_model
from flagging_site.data.model import reach_5_model
from flask_restful import Resource, Api

from flask import request

bp = Blueprint('flagging', __name__)
api = Api(bp)


def stylize_model_output(df: pd.DataFrame):
    """
    This function function stylizes the dataframe that we will output for our
    web page

    Args:
        data frame

    Returns:
        Dataframe with properties set for color, border-style, flag colors, and
        border-width
    """

    def color_flags(x):
        return 'color: blue' if x is True \
            else 'color: red' if x is False \
            else ''
    return '<div class="table-wrapper">' + \
           df.to_html(index=False) + \
           '</div>'
    # return '<div class="table-wrapper">' + (
    #     df
    #         .style
    #         .hide_index()
    #         .set_properties(**{
    #         'border-color': '#888888',
    #         'border-style': 'solid',
    #         'border-width': '1px'
    #     })
    #         .applymap(color_flags)
    #         .render()
    # ) + '</div>'


def add_to_dict(models, df, reach) -> None:
    """
    Iterates through dataframe from model output, adds to model dict where
    key equals column name, value equals column values as list type

    args:
        models: dictionary
        df: pd.DataFrame
        reach:int

    returns: None
        """
    # converts time column to type string because of conversion to json error
    df['time'] = df['time'].astype(str)
    models[f'model_{reach}'] = df.to_dict(orient='list')


@bp.route('/')
def index() -> str:
    """
    Retrieves data from hobolink and usgs and processes data, then displays data 
    on `index_model.html`     

    returns: render model on index.html
    """
    df_hobolink = get_hobolink_data('code_for_boston_export_21d')
    df_usgs = get_usgs_data()
    df = process_data(df_hobolink, df_usgs)
    flags = {
        2: reach_2_model(df, rows=1)['r2_safe'].iloc[0],
        3: reach_3_model(df, rows=1)['r3_safe'].iloc[0],
        4: reach_4_model(df, rows=1)['r4_safe'].iloc[0],
        5: reach_5_model(df, rows=1)['r5_safe'].iloc[0]
    }
    return render_template('index.html', flags=flags)

@bp.route('/output_model', methods = ["GET"])
def output_model() -> str:
    """
    Retrieves data from hobolink and usgs and processes data and then
    displays data on 'output_model.html'

    args: no argument

    returns: render model on output_model.html
    """

    #parse contents of the query string to get reach & hours parameter
    #default is  reach = 0 and hours = 24
    reach = request.args.get('reach', 0)
    hours = request.args.get('hours', 24)
        
    #convert to integers
    hours = int(hours)
    reach = int(reach)
    
    df_hobolink = get_hobolink_data('code_for_boston_export_21d')
    df_usgs = get_usgs_data()
    df = process_data(df_hobolink, df_usgs)
    
    reach_model_mapping = {
        2: reach_2_model,
        3: reach_3_model,
        4: reach_4_model,
        5: reach_5_model
    }
    
    if reach in reach_model_mapping:
        reach_func = reach_model_mapping[reach]
        reach_list = [reach_func(df, rows = hours)]
    else:
        reach_list = [
            reach_2_model(df, rows = hours),
            reach_3_model(df, rows = hours),
            reach_4_model(df, rows = hours),
            reach_5_model(df, rows = hours)
        ]
    
    table_html = '<br /><br />'.join(map(stylize_model_output, reach_list))
    
    return render_template('output_model.html', tables=table_html)


class ReachApi(Resource):
    def model_api(self) -> dict:
        """
        Class method that retrieves data from hobolink and usgs and processes
        data, then creates json-like dictionary structure for model output.

        returns: json-like dictionary
        """
        df_hobolink = get_hobolink_data('code_for_boston_export_21d')
        df_usgs = get_usgs_data()
        df = process_data(df_hobolink, df_usgs)
        dfs = {
            2: reach_2_model(df),
            3: reach_3_model(df),
            4: reach_4_model(df),
            5: reach_5_model(df)
        }
        main = {}
        models = {}
        # adds metadata
        main['version'] = '2020'
        main['time_returned'] = str(pd.to_datetime('today'))

        for reach, df in dfs.items():
            add_to_dict(models, df, reach)
        # adds models dict to main dict
        main['models'] = models

        return main

    def get(self):
        return self.model_api()


api.add_resource(ReachApi, '/api/v1/model')
