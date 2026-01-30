import React, { createContext, useContext, useState, type ReactNode } from 'react';
import api from '../services/api';

// Define Instance type directly to bypass cache issues
interface Instance {
  id: string;
  name: string | null;
  status: string;
  public_ip: string | null;
  ec2_instance_id: string | null;
  vnc_port: number;
  cloudbot_port: number;
  created_at: string;
}

interface InstanceContextType {
  instances: Instance[];
  selectedInstance: Instance | null;
  loading: boolean;
  fetchInstances: () => Promise<void>;
  createInstance: (name?: string, instanceType?: string, apiKeys?: Record<string, string>) => Promise<Instance>;
  deleteInstance: (id: string) => Promise<void>;
  selectInstance: (instance: Instance | null) => void;
  refreshInstance: (id: string) => Promise<void>;
}

const InstanceContext = createContext<InstanceContextType | undefined>(undefined);

export const InstanceProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [instances, setInstances] = useState<Instance[]>([]);
  const [selectedInstance, setSelectedInstance] = useState<Instance | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchInstances = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/instances');
      setInstances(response.data.instances);
    } catch (error) {
      console.error('Failed to fetch instances:', error);
    } finally {
      setLoading(false);
    }
  };

  const createInstance = async (name?: string, instanceType?: string, apiKeys?: Record<string, string>): Promise<Instance> => {
    const response = await api.post('/api/instances', {
      name,
      instance_type: instanceType || 't3.large',
      api_keys: apiKeys
    });
    const newInstance = response.data;
    setInstances((prev) => [newInstance, ...prev]);
    return newInstance;
  };

  const deleteInstance = async (id: string) => {
    await api.delete(`/api/instances/${id}`);
    setInstances((prev) => prev.filter((inst) => inst.id !== id));
    if (selectedInstance?.id === id) {
      setSelectedInstance(null);
    }
  };

  const selectInstance = (instance: Instance | null) => {
    setSelectedInstance(instance);
  };

  const refreshInstance = async (id: string) => {
    try {
      const response = await api.get(`/api/instances/${id}`);
      const updated = response.data;
      setInstances((prev) =>
        prev.map((inst) => (inst.id === id ? updated : inst))
      );
      if (selectedInstance?.id === id) {
        setSelectedInstance(updated);
      }
    } catch (error) {
      console.error('Failed to refresh instance:', error);
    }
  };

  return (
    <InstanceContext.Provider
      value={{
        instances,
        selectedInstance,
        loading,
        fetchInstances,
        createInstance,
        deleteInstance,
        selectInstance,
        refreshInstance,
      }}
    >
      {children}
    </InstanceContext.Provider>
  );
};

export const useInstances = () => {
  const context = useContext(InstanceContext);
  if (context === undefined) {
    throw new Error('useInstances must be used within an InstanceProvider');
  }
  return context;
};
