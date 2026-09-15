export type User = {
  id: string;
  username: string;
  name: string;
};

export type LoginRequest = {
  username: string;
  password: string;
};

export type RegisterRequest = {
  username: string;
  password: string;
  name: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};
