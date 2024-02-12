from flask import Flask, render_template, request
import pandas as pd
import plotly.graph_objects as go

app = Flask(__name__)

data_path = 'output_flattened.xlsx'

data = pd.read_excel(data_path)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analytics', methods=['GET', 'POST'])
def analytics():
    default_N = 5
    # Default selections
    if request.method == 'POST':
        N = request.form.get('N', default_N, type=int)
        selection = request.form.get('selection', 'top')
        gender = request.form.get('gender', 'male')
    else:
        N = default_N
        selection = 'top'
        gender = 'male'

      # Calculate turnout percentage and add it as a new column
    if gender == 'overall':
        data['Turnout Percentage'] = (data['Total'] / data['Total No.of Electors']) * 100
        turnout_col = 'Turnout Percentage'
    elif gender == 'male':
        data['Turnout Percentage'] = (data['Male Turnout'] / data['Total No.of Electors']) * 100
        turnout_col = 'Turnout Percentage'
    else:  # female
        data['Turnout Percentage'] = (data['Female Turnout'] / data['Total No.of Electors']) * 100
        turnout_col = 'Turnout Percentage'
    # Filter data based on selection
##    if gender == 'overall':
##        selected_data = data.nlargest(N, 'Total') if selection == 'top' else data.nsmallest(N, 'Total')
##        turnout_col = 'Total'
##    elif gender == 'male':
##        selected_data = data.nlargest(N, 'Male Turnout') if selection == 'top' else data.nsmallest(N, 'Male Turnout')
##        turnout_col = 'Male Turnout'
##    else:
##        selected_data = data.nlargest(N, 'Female Turnout') if selection == 'top' else data.nsmallest(N, 'Female Turnout')
##        turnout_col = 'Female Turnout'
    if selection == 'top':
        selected_data = data.nlargest(N, 'Turnout Percentage')
    else:  # bottom
        selected_data = data.nsmallest(N, 'Turnout Percentage')

    selected_data = selected_data.sort_values(by='Turnout Percentage', ascending=False)

    #total_turnout = selected_data[turnout_col].sum()
    if gender =='overall':
        total_turnout = data['Male Turnout'].sum()+data['Female Turnout'].sum()
    elif gender == 'male':
        total_turnout = data['Male Turnout'].sum()
    else:
        total_turnout = data['Female Turnout'].sum()
    #selected_data['Percentage'] = (selected_data[turnout_col] / total_turnout) * 100

    overall_turnout=data['Male Turnout'].sum()+data['Female Turnout'].sum()


    base_height_per_bar = 40  # Set the height per bar, adjust as needed.
    min_height = 400  # Set a minimum height for the figure.
    dynamic_height = max(min_height, len(selected_data) * base_height_per_bar)

    fig = go.Figure()
    max_value = max(selected_data['Turnout Percentage'])
    for _, row in selected_data.iterrows():
        percentage_text = f"{row[turnout_col]:.1f}%"
        voters_text = f"{gender.capitalize()} Voters-{int(row['Male Turnout' if gender == 'male' else 'Female Turnout' if gender == 'female' else 'Total'])} / Total Electors-{int(row['Total No.of Electors'])}"
        fig.add_trace(go.Bar(
            y=[row['Name']],
            x=[row[turnout_col]],
            #text=[f"{row[turnout_col]}%"],
            text=[voters_text],
            name=row['Name'],
            orientation='h',
            #marker_color='blue' if gender == 'male' else 'pink',
            marker_color='#063970' if gender == 'male' else '#501B1D' if gender == 'female' else 'purple',
            textposition='inside',
        ))

        fig.add_annotation(
            x=row[turnout_col] + (0.01 * max(selected_data[turnout_col])),
            y=row['Name'],
            text=percentage_text,
            showarrow=False,
            font=dict(
                color="#333",
                size=14
            ),
            xanchor='left',
            yanchor='middle'
        )


    fig.update_layout(
        title=f"{selection.capitalize()} {N} {gender.capitalize()} Turnout Percentage",
        xaxis_title="Turnout",
        yaxis_title="Polling Station Name",
        #barmode='stack',
        showlegend=False,
        autosize=True,
        barmode='group',
        transition={'duration': 500},
        margin=dict(l=60, r=60, t=50, b=50),
        yaxis={'categoryorder':'total ascending'},
        height=dynamic_height
    )

    graphJSON = fig.to_json()

    return render_template('analytics.html', graphJSON=graphJSON, N=N, selection=selection, gender=gender,selected_turnout=total_turnout, total_turnout=overall_turnout)

if __name__ == '__main__':
    app.run(debug=True)
