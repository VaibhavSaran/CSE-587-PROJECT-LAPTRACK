import axios from 'axios';

const BASE_URL = 'http://localhost:5001';
const LAPTOPS_API_URL = `${BASE_URL}/laptops`;

export const getLaptops = async (page,limit) => {
  try {
    const response = await axios.get(LAPTOPS_API_URL, {
        params: {
          page,
          limit
        }});
        
    return response.data;
  } catch (error) {
    console.error('Error fetching laptop data:', error);
    return [];
  }
};

export const getLaptopById = async (id) => {
  try {
    const response = await axios.get(`${LAPTOPS_API_URL}/${id}`);
    
    return response.data;
  } catch (error) {
    console.error('Error fetching laptop details:', error);
    return null;
  }
};

export const getRecommendedLaptops = async (laptopId) => {
  try{
    const response = await axios.get(`${BASE_URL}/get_recommendations/${laptopId}`);
    
    return response.data
  }catch(error){
    console.error('Error fetching recommended laptop details:', error)
    return null;
  }
}