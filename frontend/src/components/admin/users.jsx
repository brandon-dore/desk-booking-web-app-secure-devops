import {
  BooleanField,
  BooleanInput,
  Create,
  Datagrid,
  Edit,
  EmailField,
  List,
  PasswordInput,
  SimpleForm,
  TextField,
  TextInput,
} from "react-admin";

export const UserList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <TextField source="username" />
      <EmailField source="email" />
      <BooleanField source="admin" />
    </Datagrid>
  </List>
);

export const UserEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="username" />
      <TextInput source="email" />
      <BooleanInput source="admin" />
    </SimpleForm>
  </Edit>
);

export const UserCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="username" />
      <TextInput source="email" />
      <BooleanInput source="admin" />
      <PasswordInput source="password" />
    </SimpleForm>
  </Create>
);
