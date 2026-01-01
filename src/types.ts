/**
 * Type definitions for Farm Survey Application
 */

export interface GeoLocation {
  latitude: number;
  longitude: number;
}

export interface FarmSurvey {
  survey_id: number;
  farmer_name: string;
  crop_type: string;
  geo_location: GeoLocation;
  sync_status: boolean;
  last_updated: string; // ISO 8601 datetime string
  trees?: Tree[];
}

export interface FarmSurveyCreate {
  farmer_name: string;
  crop_type: string;
  geo_location: GeoLocation;
  sync_status?: boolean;
}

export interface FarmSurveyUpdate {
  farmer_name?: string;
  crop_type?: string;
  geo_location?: GeoLocation;
  sync_status?: boolean;
}

export interface Tree {
  tree_id: number;
  survey_id: number;
  species_name: string;
  tree_count: number;
  height_avg?: number | null;
  diameter_avg?: number | null;
  age_avg?: number | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface TreeCreate {
  species_name: string;
  tree_count: number;
  height_avg?: number | null;
  diameter_avg?: number | null;
  age_avg?: number | null;
  notes?: string | null;
}

export interface TreeUpdate {
  species_name?: string;
  tree_count?: number;
  height_avg?: number | null;
  diameter_avg?: number | null;
  age_avg?: number | null;
  notes?: string | null;
}

export interface ApiError {
  detail: string;
}

