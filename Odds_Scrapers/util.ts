import { default as axios, AxiosRequestConfig, AxiosInstance } from "axios";
import * as moment from "moment";

export const format = (date: moment.MomentInput, format: string) => {
  return moment(date).format(format);
};

export const parse = (date: string, format: string) => {
  return moment(date, format).toDate();
};

export const get = async <T>(
  url: string,
  args?: AxiosRequestConfig
): Promise<T> => {
  const response = await axios.get(url, args);
  return response.data;
};
