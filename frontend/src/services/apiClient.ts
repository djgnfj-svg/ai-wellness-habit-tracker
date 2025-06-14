import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL, STORAGE_KEYS, HTTP_STATUS } from '../../constants';
import { ApiResponse, ApiError } from '../../types';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // 요청 인터셉터 - 토큰 자동 첨부
    this.client.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem(STORAGE_KEYS.USER_TOKEN);
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        // 디버깅용 로그 (개발 환경에서만)
        if (__DEV__) {
          console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
          if (config.data) {
            console.log('📤 Request Data:', config.data);
          }
        }
        
        return config;
      },
      (error) => {
        if (__DEV__) {
          console.error('❌ Request Error:', error);
        }
        return Promise.reject(error);
      }
    );

    // 응답 인터셉터 - 에러 처리 및 토큰 갱신
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        if (__DEV__) {
          console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        }
        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        if (__DEV__) {
          console.error('❌ API Error:', {
            status: error.response?.status,
            url: error.config?.url,
            message: error.response?.data?.message || error.message,
          });
        }

        // 401 에러이고 토큰 갱신 요청이 아닌 경우
        if (
          error.response?.status === HTTP_STATUS.UNAUTHORIZED &&
          !originalRequest._retry &&
          !originalRequest.url?.includes('/auth/refresh')
        ) {
          originalRequest._retry = true;

          try {
            const refreshToken = await AsyncStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
            if (refreshToken) {
              const response = await this.client.post('/auth/refresh', {
                refresh_token: refreshToken,
              });

              const { access_token, refresh_token: newRefreshToken } = response.data;
              
              // 새로운 토큰 저장
              await AsyncStorage.setItem(STORAGE_KEYS.USER_TOKEN, access_token);
              await AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, newRefreshToken);

              // 원래 요청에 새 토큰 적용
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            // 토큰 갱신 실패 시 로그아웃 처리
            await this.clearAuthData();
            // 여기서 로그인 화면으로 리다이렉트하거나 이벤트 발생
            throw refreshError;
          }
        }

        return Promise.reject(this.handleError(error));
      }
    );
  }

  private async clearAuthData() {
    await AsyncStorage.multiRemove([
      STORAGE_KEYS.USER_TOKEN,
      STORAGE_KEYS.REFRESH_TOKEN,
      STORAGE_KEYS.USER_PROFILE,
    ]);
  }

  private handleError(error: any): ApiError {
    if (error.response) {
      // 서버 응답이 있는 경우
      const { data, status } = error.response;
      return {
        message: data?.message || '서버 오류가 발생했습니다.',
        code: data?.code || status.toString(),
        details: data?.details || {},
      };
    } else if (error.request) {
      // 네트워크 오류
      return {
        message: '네트워크 연결을 확인해주세요.',
        code: 'NETWORK_ERROR',
      };
    } else {
      // 기타 오류
      return {
        message: error.message || '알 수 없는 오류가 발생했습니다.',
        code: 'UNKNOWN_ERROR',
      };
    }
  }

  // HTTP 메서드들
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<ApiResponse<T>>(url, config);
    return response.data.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<ApiResponse<T>>(url, data, config);
    return response.data.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<ApiResponse<T>>(url, data, config);
    return response.data.data;
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch<ApiResponse<T>>(url, data, config);
    return response.data.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<ApiResponse<T>>(url, config);
    return response.data.data;
  }

  // 파일 업로드
  async uploadFile<T>(
    url: string, 
    file: FormData, 
    onUploadProgress?: (progress: number) => void
  ): Promise<T> {
    const response = await this.client.post<ApiResponse<T>>(url, file, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onUploadProgress && progressEvent.total) {
          const progress = (progressEvent.loaded / progressEvent.total) * 100;
          onUploadProgress(Math.round(progress));
        }
      },
    });
    return response.data.data;
  }

  // 원시 axios 인스턴스 접근 (필요한 경우)
  getAxiosInstance(): AxiosInstance {
    return this.client;
  }
}

// 싱글톤 인스턴스
export const apiClient = new ApiClient();
export default apiClient;