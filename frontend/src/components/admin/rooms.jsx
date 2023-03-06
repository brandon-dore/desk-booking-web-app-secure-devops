import {
  Create,
  Datagrid,
  Edit,
  List,
  SimpleForm,
  TextField,
  TextInput,
} from "react-admin";

export const RoomList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <TextField source="name" />
    </Datagrid>
  </List>
);

export const RoomEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="name" />
    </SimpleForm>
  </Edit>
);

export const RoomCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="name" />
    </SimpleForm>
  </Create>
);
