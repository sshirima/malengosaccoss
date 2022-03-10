const renderChart = (canvas, data, labels)=>{
    const ctx = document.getElementById(canvas).getContext('2d');
    const myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
            label: 'Monthly shares last 6 months',
            data: data,
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        title :{
            display: true,
            text: 'Shares'
        }, 
        scales: {
            y: {
              beginAtZero: true
            }
          }
    }
});
}

const getChartdata = (canvas, url)=>{
    fetch(url)
    .then(res=>res.json())
    .then((data)=>{
        var chart_labels = [];
        var chart_data = [];

        data.forEach(element => {
            chart_labels.push(element.month)
            chart_data.push(element.sum)
        });
        renderChart(canvas, chart_data, chart_labels)
    })
}

document.onload = getChartdata('savings_chart','get-savings')
document.onload = getChartdata('shares_chart','get-shares')