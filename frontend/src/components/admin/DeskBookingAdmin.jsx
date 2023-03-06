// in src/App.js
import { useEffect, useState } from "react";

import AssignmentIcon from "@mui/icons-material/Assignment";
import DesktopWindowsIcon from "@mui/icons-material/DesktopWindows";
import UserIcon from "@mui/icons-material/Group";
import MeetingRoomIcon from "@mui/icons-material/MeetingRoom";
import { Box, Container, CssBaseline, Typography } from "@mui/material";
import { isEqual, isObject, transform } from "lodash";
import simpleRestDataProvider from "ra-data-simple-rest";

import { Admin, fetchUtils, Layout, Resource } from "react-admin";
import TopBar from "../header/CommonAppBar";
import APIService from "../services/api.service";
import { BookingCreate, BookingEdit, BookingList } from "./bookings";
import Dashboard from "./Dashboard";
import { DeskCreate, DeskEdit, DeskList } from "./desks";
import { RoomCreate, RoomEdit, RoomList } from "./rooms";
import { UserCreate, UserEdit, UserList } from "./users";

// const httpClient = fetchUtils.fetchJson;

const httpClient = (url, options = {}) => {
  if (!options.headers) {
    options.headers = new Headers({ Accept: "application/json" });
  }
  const token = JSON.parse(localStorage.getItem("user"));
  options.headers.set("Authorization", `Bearer ${token.access_token}`);
  return fetchUtils.fetchJson(url, options);
};

const baseDataProvider = simpleRestDataProvider(
  "http://localhost:8000",
  httpClient
);

const diff = (object, base) => {
  return transform(object, (result, value, key) => {
    if (!isEqual(value, base[key])) {
      result[key] =
        isObject(value) && isObject(base[key]) ? diff(value, base[key]) : value;
    }
  });
};

export const dataProvider = {
  ...baseDataProvider,
  update: (resource, params) =>
    httpClient(`http://localhost:8000/${resource}/${params.id}`, {
      method: "PATCH",
      body: JSON.stringify(diff(params.data, params.previousData)),
      headers: new Headers({
        Authorization:
          "Bearer " + JSON.parse(localStorage.getItem("user")).access_token,
      }),
    }).then(({ json }) => ({ data: json })),
};

const MyLayout = (props) => <Layout {...props} appBar={TopBar} />;

export const DeskBookingAdmin = () => {
  const [isAdmin, setIsAdmin] = useState(undefined);

  useEffect(() => {
    APIService.getUserInfo().then(
      (response) => {
        setIsAdmin(response.data.admin);
      },
      (error) => {
        console.log(error);
      }
    );
  }, []);

  return (
    <>
      {!isAdmin && (
        <>
          <TopBar fixed="true" />
          <Container component="main" maxWidth="xs">
            <CssBaseline />
            <Box
              sx={{
                marginTop: 8,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                textTransform: "uppercase",
                textAlign: "center",
                fontWeight: "bold",
              }}
            >
              <Typography component="h1" variant="h5">
                You need to be an admin to view this page
              </Typography>
            </Box>
          </Container>
        </>
      )}
      {isAdmin && (
        <Admin
          basename="/admin"
          dashboard={Dashboard}
          dataProvider={dataProvider}
          layout={MyLayout}
        >
          <Resource
            name="users"
            list={UserList}
            edit={UserEdit}
            create={UserCreate}
            icon={UserIcon}
          />
          <Resource
            name="bookings"
            list={BookingList}
            edit={BookingEdit}
            create={BookingCreate}
            icon={AssignmentIcon}
          />
          <Resource
            name="rooms"
            list={RoomList}
            edit={RoomEdit}
            create={RoomCreate}
            icon={MeetingRoomIcon}
          />
          <Resource
            name="desks"
            list={DeskList}
            edit={DeskEdit}
            create={DeskCreate}
            icon={DesktopWindowsIcon}
          />
        </Admin>
      )}
    </>
  );
};
