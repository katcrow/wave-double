// Generated from Supabase project qqhjeumlecaudsiqhhdu on 2026-09-02. Do not edit by hand.
export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.5"
  }
  public: {
    Tables: {
      analysis_inputs: {
        Row: {
          analysis_session_id: string
          collected_at: string | null
          created_at: string
          id: string
          input_snapshot_json: Json
          input_type: string
          source_mode: string | null
          user_id: string
        }
        Insert: {
          analysis_session_id: string
          collected_at?: string | null
          created_at?: string
          id?: string
          input_snapshot_json: Json
          input_type: string
          source_mode?: string | null
          user_id: string
        }
        Update: {
          analysis_session_id?: string
          collected_at?: string | null
          created_at?: string
          id?: string
          input_snapshot_json?: Json
          input_type?: string
          source_mode?: string | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "analysis_inputs_analysis_session_user_id_fkey"
            columns: ["analysis_session_id", "user_id"]
            isOneToOne: false
            referencedRelation: "analysis_sessions"
            referencedColumns: ["id", "user_id"]
          },
        ]
      }
      analysis_inputs_cache: {
        Row: {
          created_at: string
          domestic_market: Json | null
          global_market: Json | null
          id: string
          leader_candidates: Json | null
          market_status: Json | null
          sector_breadth: Json | null
          sector_universe: Json | null
          snapshot_at: string
          source_trigger: string
          subject_flow: Json | null
          theme_universe: Json | null
          time_mode: string
          trade_date: string
          user_id: string
        }
        Insert: {
          created_at?: string
          domestic_market?: Json | null
          global_market?: Json | null
          id?: string
          leader_candidates?: Json | null
          market_status?: Json | null
          sector_breadth?: Json | null
          sector_universe?: Json | null
          snapshot_at?: string
          source_trigger: string
          subject_flow?: Json | null
          theme_universe?: Json | null
          time_mode: string
          trade_date: string
          user_id: string
        }
        Update: {
          created_at?: string
          domestic_market?: Json | null
          global_market?: Json | null
          id?: string
          leader_candidates?: Json | null
          market_status?: Json | null
          sector_breadth?: Json | null
          sector_universe?: Json | null
          snapshot_at?: string
          source_trigger?: string
          subject_flow?: Json | null
          theme_universe?: Json | null
          time_mode?: string
          trade_date?: string
          user_id?: string
        }
        Relationships: []
      }
      analysis_outputs: {
        Row: {
          analysis_session_id: string
          created_at: string
          decision_label: string | null
          id: string
          market_probability: number | null
          output_snapshot_json: Json | null
          sector_probability: number | null
          stock_probability: number | null
          user_id: string
        }
        Insert: {
          analysis_session_id: string
          created_at?: string
          decision_label?: string | null
          id?: string
          market_probability?: number | null
          output_snapshot_json?: Json | null
          sector_probability?: number | null
          stock_probability?: number | null
          user_id: string
        }
        Update: {
          analysis_session_id?: string
          created_at?: string
          decision_label?: string | null
          id?: string
          market_probability?: number | null
          output_snapshot_json?: Json | null
          sector_probability?: number | null
          stock_probability?: number | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "analysis_outputs_analysis_session_user_id_fkey"
            columns: ["analysis_session_id", "user_id"]
            isOneToOne: false
            referencedRelation: "analysis_sessions"
            referencedColumns: ["id", "user_id"]
          },
        ]
      }
      analysis_run_locks: {
        Row: {
          created_at: string
          expires_at: string
          trigger_type: string
          user_id: string
        }
        Insert: {
          created_at?: string
          expires_at: string
          trigger_type?: string
          user_id: string
        }
        Update: {
          created_at?: string
          expires_at?: string
          trigger_type?: string
          user_id?: string
        }
        Relationships: []
      }
      analysis_sessions: {
        Row: {
          buy_flag: string | null
          created_at: string
          freshness: string | null
          id: string
          integrity: string | null
          market_state: string | null
          reason_summary_json: Json | null
          selected_axis: string | null
          server_time: string | null
          source_mode: string | null
          time_mode: string | null
          trigger_type: string | null
          updated_at: string
          user_id: string
        }
        Insert: {
          buy_flag?: string | null
          created_at?: string
          freshness?: string | null
          id?: string
          integrity?: string | null
          market_state?: string | null
          reason_summary_json?: Json | null
          selected_axis?: string | null
          server_time?: string | null
          source_mode?: string | null
          time_mode?: string | null
          trigger_type?: string | null
          updated_at?: string
          user_id: string
        }
        Update: {
          buy_flag?: string | null
          created_at?: string
          freshness?: string | null
          id?: string
          integrity?: string | null
          market_state?: string | null
          reason_summary_json?: Json | null
          selected_axis?: string | null
          server_time?: string | null
          source_mode?: string | null
          time_mode?: string | null
          trigger_type?: string | null
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      analysis_stage_events: {
        Row: {
          analysis_session_id: string
          completed_at: string | null
          created_at: string
          error_code: string | null
          error_message: string | null
          id: string
          request_id: string
          retry_count: number
          stage: string
          started_at: string | null
          status: string
          user_id: string
        }
        Insert: {
          analysis_session_id: string
          completed_at?: string | null
          created_at?: string
          error_code?: string | null
          error_message?: string | null
          id?: string
          request_id?: string
          retry_count?: number
          stage: string
          started_at?: string | null
          status: string
          user_id: string
        }
        Update: {
          analysis_session_id?: string
          completed_at?: string | null
          created_at?: string
          error_code?: string | null
          error_message?: string | null
          id?: string
          request_id?: string
          retry_count?: number
          stage?: string
          started_at?: string | null
          status?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "analysis_stage_events_analysis_session_user_id_fkey"
            columns: ["analysis_session_id", "user_id"]
            isOneToOne: false
            referencedRelation: "analysis_sessions"
            referencedColumns: ["id", "user_id"]
          },
        ]
      }
      api_capability_snapshots: {
        Row: {
          created_at: string
          id: string
          snapshot_json: Json
          user_id: string
          verified_at: string | null
        }
        Insert: {
          created_at?: string
          id?: string
          snapshot_json: Json
          user_id: string
          verified_at?: string | null
        }
        Update: {
          created_at?: string
          id?: string
          snapshot_json?: Json
          user_id?: string
          verified_at?: string | null
        }
        Relationships: []
      }
      candidate_source_contrib: {
        Row: {
          attempt_run_id: string
          candidate_id: string
          contribution_weight: number
          source: string
        }
        Insert: {
          attempt_run_id: string
          candidate_id: string
          contribution_weight: number
          source: string
        }
        Update: {
          attempt_run_id?: string
          candidate_id?: string
          contribution_weight?: number
          source?: string
        }
        Relationships: [
          {
            foreignKeyName: "candidate_source_contrib_attempt_run_id_fkey"
            columns: ["attempt_run_id"]
            isOneToOne: false
            referencedRelation: "runs"
            referencedColumns: ["run_id"]
          },
          {
            foreignKeyName: "candidate_source_contrib_candidate_id_attempt_run_id_fkey"
            columns: ["candidate_id", "attempt_run_id"]
            isOneToOne: false
            referencedRelation: "candidates"
            referencedColumns: ["candidate_id", "attempt_run_id"]
          },
        ]
      }
      candidates: {
        Row: {
          attempt_run_id: string
          candidate_id: string
          name: string | null
          ticker: string
          trading_day: string
          trading_value: number
          truncated: boolean
        }
        Insert: {
          attempt_run_id: string
          candidate_id?: string
          name?: string | null
          ticker: string
          trading_day: string
          trading_value: number
          truncated?: boolean
        }
        Update: {
          attempt_run_id?: string
          candidate_id?: string
          name?: string | null
          ticker?: string
          trading_day?: string
          trading_value?: number
          truncated?: boolean
        }
        Relationships: [
          {
            foreignKeyName: "candidates_attempt_run_id_fkey"
            columns: ["attempt_run_id"]
            isOneToOne: false
            referencedRelation: "runs"
            referencedColumns: ["run_id"]
          },
        ]
      }
      dispatch_outbox: {
        Row: {
          attempts: number
          created_at: string
          dispatch_request_id: string
          github_run_id: number | null
          lease_expires_at: string | null
          lease_token: string | null
          outbox_id: string
          run_id: string | null
          status: string
          updated_at: string
        }
        Insert: {
          attempts?: number
          created_at?: string
          dispatch_request_id: string
          github_run_id?: number | null
          lease_expires_at?: string | null
          lease_token?: string | null
          outbox_id?: string
          run_id?: string | null
          status?: string
          updated_at?: string
        }
        Update: {
          attempts?: number
          created_at?: string
          dispatch_request_id?: string
          github_run_id?: number | null
          lease_expires_at?: string | null
          lease_token?: string | null
          outbox_id?: string
          run_id?: string | null
          status?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "dispatch_outbox_dispatch_request_id_fkey"
            columns: ["dispatch_request_id"]
            isOneToOne: true
            referencedRelation: "dispatch_request"
            referencedColumns: ["dispatch_request_id"]
          },
          {
            foreignKeyName: "dispatch_outbox_run_id_fkey"
            columns: ["run_id"]
            isOneToOne: false
            referencedRelation: "runs"
            referencedColumns: ["run_id"]
          },
        ]
      }
      dispatch_request: {
        Row: {
          created_at: string
          dispatch_request_id: string
          idempotency_key: string
          logical_run_key: string
          payload_hash: string
          requested_by: string
        }
        Insert: {
          created_at?: string
          dispatch_request_id?: string
          idempotency_key: string
          logical_run_key: string
          payload_hash: string
          requested_by: string
        }
        Update: {
          created_at?: string
          dispatch_request_id?: string
          idempotency_key?: string
          logical_run_key?: string
          payload_hash?: string
          requested_by?: string
        }
        Relationships: []
      }
      feature_flags: {
        Row: {
          created_at: string
          flag_name: string
          flag_value: boolean
          id: string
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          flag_name: string
          flag_value?: boolean
          id?: string
          updated_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          flag_name?: string
          flag_value?: boolean
          id?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      logical_runs: {
        Row: {
          active_attempt_run_id: string | null
          batch_kind: string
          canonical_success_run_id: string | null
          current_complete_run_id: string | null
          latest_partial_run_id: string | null
          logical_run_key: string
          published_at: string | null
          trading_day: string
        }
        Insert: {
          active_attempt_run_id?: string | null
          batch_kind: string
          canonical_success_run_id?: string | null
          current_complete_run_id?: string | null
          latest_partial_run_id?: string | null
          logical_run_key: string
          published_at?: string | null
          trading_day: string
        }
        Update: {
          active_attempt_run_id?: string | null
          batch_kind?: string
          canonical_success_run_id?: string | null
          current_complete_run_id?: string | null
          latest_partial_run_id?: string | null
          logical_run_key?: string
          published_at?: string | null
          trading_day?: string
        }
        Relationships: [
          {
            foreignKeyName: "logical_runs_active_attempt_run_id_fkey"
            columns: ["active_attempt_run_id"]
            isOneToOne: false
            referencedRelation: "runs"
            referencedColumns: ["run_id"]
          },
          {
            foreignKeyName: "logical_runs_canonical_success_run_id_fkey"
            columns: ["canonical_success_run_id"]
            isOneToOne: false
            referencedRelation: "runs"
            referencedColumns: ["run_id"]
          },
          {
            foreignKeyName: "logical_runs_current_complete_run_id_fkey"
            columns: ["current_complete_run_id"]
            isOneToOne: false
            referencedRelation: "runs"
            referencedColumns: ["run_id"]
          },
          {
            foreignKeyName: "logical_runs_latest_partial_run_id_fkey"
            columns: ["latest_partial_run_id"]
            isOneToOne: false
            referencedRelation: "runs"
            referencedColumns: ["run_id"]
          },
        ]
      }
      parameter_profiles: {
        Row: {
          created_at: string
          id: string
          is_active: boolean
          name: string
          parameters_json: Json
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          id?: string
          is_active?: boolean
          name?: string
          parameters_json: Json
          updated_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          id?: string
          is_active?: boolean
          name?: string
          parameters_json?: Json
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      parameter_revisions: {
        Row: {
          change_reason: string | null
          created_at: string
          id: string
          parameter_profile_id: string
          parameters_json: Json
          revision_number: number
          user_id: string
        }
        Insert: {
          change_reason?: string | null
          created_at?: string
          id?: string
          parameter_profile_id: string
          parameters_json: Json
          revision_number: number
          user_id: string
        }
        Update: {
          change_reason?: string | null
          created_at?: string
          id?: string
          parameter_profile_id?: string
          parameters_json?: Json
          revision_number?: number
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "parameter_revisions_parameter_profile_user_id_fkey"
            columns: ["parameter_profile_id", "user_id"]
            isOneToOne: false
            referencedRelation: "parameter_profiles"
            referencedColumns: ["id", "user_id"]
          },
        ]
      }
      profiles: {
        Row: {
          created_at: string
          id: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          id: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          id?: string
          updated_at?: string
        }
        Relationships: []
      }
      runs: {
        Row: {
          attempt_no: number
          excluded_count: number | null
          fallback_used: boolean
          fence_token: number
          finished_at: string | null
          lease_expires_at: string
          lease_token: string
          logical_run_key: string
          original_count: number | null
          run_id: string
          selection_input_hash: string | null
          skip_reason: string | null
          stage_results: Json
          stage_status: Json
          started_at: string
          status: string
          trigger: string
          truncated_count: number
          unprocessed_count: number
        }
        Insert: {
          attempt_no: number
          excluded_count?: number | null
          fallback_used?: boolean
          fence_token: number
          finished_at?: string | null
          lease_expires_at: string
          lease_token?: string
          logical_run_key: string
          original_count?: number | null
          run_id?: string
          selection_input_hash?: string | null
          skip_reason?: string | null
          stage_results?: Json
          stage_status?: Json
          started_at?: string
          status: string
          trigger: string
          truncated_count?: number
          unprocessed_count?: number
        }
        Update: {
          attempt_no?: number
          excluded_count?: number | null
          fallback_used?: boolean
          fence_token?: number
          finished_at?: string | null
          lease_expires_at?: string
          lease_token?: string
          logical_run_key?: string
          original_count?: number | null
          run_id?: string
          selection_input_hash?: string | null
          skip_reason?: string | null
          stage_results?: Json
          stage_status?: Json
          started_at?: string
          status?: string
          trigger?: string
          truncated_count?: number
          unprocessed_count?: number
        }
        Relationships: [
          {
            foreignKeyName: "runs_logical_run_key_fkey"
            columns: ["logical_run_key"]
            isOneToOne: false
            referencedRelation: "logical_runs"
            referencedColumns: ["logical_run_key"]
          },
        ]
      }
      scheduled_data_cache: {
        Row: {
          cache_type: string
          collected_at: string
          id: string
          payload_json: Json
          tr_code: string
          trade_date: string
          user_id: string
        }
        Insert: {
          cache_type: string
          collected_at?: string
          id?: string
          payload_json: Json
          tr_code: string
          trade_date: string
          user_id: string
        }
        Update: {
          cache_type?: string
          collected_at?: string
          id?: string
          payload_json?: Json
          tr_code?: string
          trade_date?: string
          user_id?: string
        }
        Relationships: []
      }
      sector_flow_daily: {
        Row: {
          certify_score: number | null
          collected_at: string
          id: string
          leader_hname: string | null
          sector_code: string
          sector_name: string
          sector_rank: number
          snapshot_at: string
          trade_date: string
          user_id: string
        }
        Insert: {
          certify_score?: number | null
          collected_at?: string
          id?: string
          leader_hname?: string | null
          sector_code: string
          sector_name: string
          sector_rank: number
          snapshot_at: string
          trade_date: string
          user_id: string
        }
        Update: {
          certify_score?: number | null
          collected_at?: string
          id?: string
          leader_hname?: string | null
          sector_code?: string
          sector_name?: string
          sector_rank?: number
          snapshot_at?: string
          trade_date?: string
          user_id?: string
        }
        Relationships: []
      }
    }
    Views: {
      cron_run_health: {
        Row: {
          last_snapshot_at: string | null
          latest_24h_snapshot_at: string | null
          runs_24h: number | null
          runs_with_payload_24h: number | null
          time_mode: string | null
        }
        Relationships: []
      }
    }
    Functions: {
      advance_dispatch_outbox: {
        Args: {
          p_github_run_id?: number
          p_lease_token: string
          p_outbox_id: string
          p_run_id?: string
          p_status: string
        }
        Returns: Json
      }
      claim_dispatch_outbox: {
        Args: { p_limit?: number; p_worker_lease_seconds?: number }
        Returns: Json
      }
      get_dashboard_snapshot: { Args: never; Returns: Json }
      get_last_auto_session_age_ms: { Args: never; Returns: number }
      heartbeat_attempt: {
        Args: {
          p_fence_token: number
          p_lease_seconds?: number
          p_lease_token: string
          p_run_id: string
        }
        Returns: Json
      }
      publish_attempt:
        | { Args: { p_fence_token: number; p_run_id: string }; Returns: Json }
        | {
            Args: {
              p_fence_token: number
              p_lease_token: string
              p_run_id: string
            }
            Returns: Json
          }
      reap_expired_attempts: { Args: { p_now?: string }; Returns: number }
      reconcile_dispatch_outbox: { Args: never; Returns: Json }
      record_dispatch_receipt: {
        Args: { p_dispatch_request_id: string; p_run_id: string }
        Returns: Json
      }
      release_analysis_lock: { Args: never; Returns: undefined }
      request_manual_dispatch: {
        Args: {
          p_batch_kind: string
          p_idempotency_key: string
          p_logical_run_key: string
          p_payload_hash: string
          p_requested_by: string
          p_trading_day: string
        }
        Returns: Json
      }
      run_analysis_retention: {
        Args: { p_retention_days?: number }
        Returns: Json
      }
      skip_attempt: {
        Args: {
          p_fence_token: number
          p_lease_token: string
          p_run_id: string
          p_skip_reason: string
        }
        Returns: Json
      }
      start_attempt: {
        Args: {
          p_batch_kind: string
          p_lease_seconds?: number
          p_logical_run_key: string
          p_trading_day: string
          p_trigger: string
        }
        Returns: Json
      }
      try_acquire_analysis_lock:
        | { Args: never; Returns: boolean }
        | { Args: { p_trigger_type?: string }; Returns: string }
      write_candidates: {
        Args: {
          p_candidates: Json
          p_fence_token: number
          p_lease_token: string
          p_metadata: Json
          p_run_id: string
        }
        Returns: Json
      }
      write_stage: {
        Args: {
          p_expected_status: string
          p_fallback_used?: boolean
          p_fence_token: number
          p_lease_token: string
          p_result?: Json
          p_run_id: string
          p_stage: string
          p_status: string
          p_unprocessed_count?: number
        }
        Returns: Json
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
