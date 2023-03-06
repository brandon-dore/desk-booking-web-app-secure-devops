// in src/Dashboard.js
import { Card, CardContent, CardHeader } from "@mui/material";

const Dashboard = () => {
  return (
    <Card sx={{ mt: 2 }}>
      <CardHeader title="Welcome to the administration dashboard" />
      <CardContent>
        This can be used to view the database in a GUI and perform all CRUD
        operations on each table. To edit a entry simply click on it, make the
        edits and hit save. Click <a href="/">here</a> to get back to the home
        page.
      </CardContent>
    </Card>
  );
};

export default Dashboard;
