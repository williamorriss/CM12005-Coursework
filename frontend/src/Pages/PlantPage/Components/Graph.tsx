import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';
import "../Styling/Graph.css";

interface DataPoint {
  datetime: Date;
  value: number;
}

interface ChartProps {
  data: DataPoint[];
  title?: string; 
  yAxisLabel?: string; 
  xAxisLabel?: string; 
}

export function TimeSeriesChart({ data, title, yAxisLabel, xAxisLabel }: ChartProps) {
  const chartData = data.map(point => ({
    datetime: format(point.datetime, 'yyyy-MM-dd HH:mm'),
    value: point.value,
    originalDate: point.datetime
  }));

  return (
    <div className="background-div">
      <h2 className="title">{title}</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart 
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 15 }} 
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff" />
          <XAxis 
            dataKey="datetime" 
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={70} 
            stroke="#ffffff"
            label={{
              value: xAxisLabel,
              position: 'insideBottom',
              style: { fill: '#ffffff', fontSize: 20 }
            }}
          />
          <YAxis 
            stroke="#ffffff"
            label={{ 
              value: yAxisLabel, 
              angle: -90, 
              position: 'insideLeft',
              style: { fill: '#ffffff', fontSize: 20 }
            }}
          />
          <Tooltip 
            labelFormatter={(label) => `Time: ${label}`}
            formatter={(value) => [`${value}`, 'Value']}
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #ccc',
              borderRadius: '4px',
              padding: '10px'
            }}
          />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke="#8884d8" 
            dot={false}
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}