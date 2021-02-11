import * as fs from "fs";

export const readFile = (path: fs.PathLike | number): Promise<Buffer> => {
  return new Promise((resolve, reject) => {
    fs.readFile(path, (error, data) => {
      if (error) {
        reject(error);
      } else {
        resolve(data);
      }
    });
  });
};

export const writeFile = (
  path: fs.PathLike | number,
  buffer: Buffer
): Promise<void> => {
  return new Promise((resolve, reject) => {
    fs.writeFile(path, buffer, (error) => {
      if (error) {
        reject(error);
      } else {
        resolve();
      }
    });
  });
};
