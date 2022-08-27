import React, { useEffect, useState } from 'react';
import TopBar from '../auth/TopBar';
import APIService from '../services/api.service';


const Home = () => {

     const [user, setUser] = useState(undefined)

     useEffect(() => {
          APIService.getUserInfo().then(
               response => {
                    setUser(response.data)
               },
               error => {
                 console.log(error);
               }
             );
     }, [])

     return (
          <>
               <TopBar />
               <h1>
                    test = {JSON.stringify(user)}
               </h1>
          </>
     )
}

export default Home;