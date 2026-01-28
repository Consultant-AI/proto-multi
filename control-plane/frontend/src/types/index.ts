export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface Instance {
  id: string;
  name: string | null;
  status: string;
  public_ip: string | null;
  ec2_instance_id: string | null;
  vnc_port: number;
  cloudbot_port: number;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface ApiKeyProvider {
  provider: string;
  created_at?: string;
}
