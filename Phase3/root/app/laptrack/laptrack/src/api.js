import axios from 'axios';

const BASE_URL = 'http://localhost:5001';
const LAPTOPS_API_URL = `${BASE_URL}/laptops`;

export const getLaptops = async (page, limit) => {
  try {
    const response = await axios.get(LAPTOPS_API_URL, {
      params: {
        page,
        limit
      }
    });

    return response.data;
  } catch (error) {
    console.error('Error fetching laptop data:', error);
    return [];
  }
};

export const getLaptopsWithSorting = async (page, limit,sortBy,order) => {
  try {
    const response = await axios.get(LAPTOPS_API_URL, {
      params: {
        page,
        limit,
        sortBy,
        order
      }
    });

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
  try {
    const response = await axios.get(`${BASE_URL}/get_recommendations/${laptopId}`);

    return response.data
  } catch (error) {
    console.error('Error fetching recommended laptop details:', error)
    return null;
  }
}

export const plotGraphsForSpecs = async (inputs) => {
  try {
    const response = await axios.post(`${BASE_URL}/plot-price-variation`, inputs)
    return response.data
  } catch (error) {
    console.error('Error plotting graphs:', error)
    return null;
  }
}

export const getBuyingOptions = async (inputs) => {
  try {
    const response = await axios.post(`${BASE_URL}/find-laptops`, inputs)
    return response.data.buying_options
  } catch (error) {
    console.error('Error plotting graphs:', error)
    return null;
  }
}

export const getPredictedPriceForSpecs = async (inputs) => {
  try {
    const response = await axios.post(`${BASE_URL}/predict-price`, inputs)
    return response.data.predicted_price
  } catch (error) {
    console.error('Error plotting graphs:', error)
    return null;
  }
}
export const updateInventoryData =async (laptopId,inputs) => {
  try{
    const response = await axios.put(`${BASE_URL}/laptops/${laptopId}`,inputs);
    console.log(response);
    return response
  }catch(error){
    console.error('Error updating laptop details');
    return null;
  }
}