import axios from 'axios';
import authHeader from './auth-header';
const API_URL = 'http://localhost:8000/';

class APIService {
  getUserInfo() {
    return axios.get(API_URL + 'users/me/', { headers: authHeader() });
  }
  getRooms() {
    return axios.get(API_URL + 'rooms', { headers: authHeader() });
  }
  getDesks() {
    return axios.get(API_URL + 'rooms', { headers: authHeader() });
  }
}

export default new APIService();