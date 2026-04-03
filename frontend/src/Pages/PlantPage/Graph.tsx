import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';
import "./PlantPage.css";

// Define your data type
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
  // Transform data for recharts
  const chartData = data.map(point => ({
    datetime: format(point.datetime, 'yyyy-MM-dd HH:mm'),
    value: point.value,
    originalDate: point.datetime
  }));

  return (
    <div className="counter-box">
      <h2>{title}</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart 
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 60 }} // Increased bottom margin
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis 
            dataKey="datetime" 
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={70} // Height for rotated labels
            stroke="#adadad"
            label={{
              value: xAxisLabel,
              position: 'insideBottom',
              offset: -5,
              style: { fill: '#adadad', fontSize: 20 }
            }}
          />
          <YAxis 
            stroke="#adadad"
            label={{ 
              value: yAxisLabel, 
              angle: -90, 
              position: 'insideLeft',
              style: { fill: '#adadad', fontSize: 20 }
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