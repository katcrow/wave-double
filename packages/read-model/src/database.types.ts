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
      bias_event_by_source: {
        Row: {
          backtest_universe_signal_count: number
          bias_event_id: string
          candidate_pop_signal_count: number
          created_at: string
          diff_count: number
          intersection_count: number
          missed_opportunity_count: number
          source: string
        }
        Insert: {
          backtest_universe_signal_count: number
          bias_event_id: string
          candidate_pop_signal_count: number
          created_at?: string
          diff_count: number
          intersection_count: number
          missed_opportunity_count: number
          source: string
        }
        Update: {
          backtest_universe_signal_count?: number
          bias_event_id?: string
          candidate_pop_signal_count?: number
          created_at?: string
          diff_count?: number
          intersection_count?: number
          missed_opportunity_count?: number
          source?: string
        }
        Relationships: [
          {
            foreignKeyName: "bias_event_by_source_bias_event_id_fkey"
            columns: ["bias_event_id"]
            isOneToOne: false
            referencedRelation: "bias_event_by_source_canonical"
            referencedColumns: ["bias_event_id"]
          },
          {
            foreignKeyName: "bias_event_by_source_bias_event_id_fkey"
            columns: ["bias_event_id"]
            isOneToOne: false
            referencedRelation: "bias_events"
            referencedColumns: ["bias_event_id"]
          },
          {
            foreignKeyName: "bias_event_by_source_bias_event_id_fkey"
            columns: ["bias_event_id"]
            isOneToOne: false
            referencedRelation: "bias_events_canonical"
            referencedColumns: ["bias_event_id"]
          },
        ]
      }
      bias_events: {
        Row: {
          bias_event_id: string
          calculation_meta: Json
          created_at: string
          logical_run_key: string
          trading_day: string
        }
        Insert: {
          bias_event_id?: string
          calculation_meta?: Json
          created_at?: string
          logical_run_key: string
          trading_day: string
        }
        Update: {
          bias_event_id?: string
          calculation_meta?: Json
          created_at?: string
          logical_run_key?: string
          trading_day?: string
        }
        Relationships: [
          {
            foreignKeyName: "bias_events_logical_run_key_fkey"
            columns: ["logical_run_key"]
            isOneToOne: false
            referencedRelation: "logical_runs"
            referencedColumns: ["logical_run_key"]
          },
        ]
      }
      candidate_outcome: {
        Row: {
          cutoff_n: number
          entry_date: string
          entry_price: number
          exit_date: string | null
          exit_price: number | null
          holding_days: number
          outcome_id: string
          return_pct: number | null
          sl_pct: number
          status: string
          strategy: string
          ticker: string
          tp_pct: number
          version: number
        }
        Insert: {
          cutoff_n?: number
          entry_date: string
          entry_price: number
          exit_date?: string | null
          exit_price?: number | null
          holding_days?: number
          outcome_id?: string
          return_pct?: number | null
          sl_pct?: number
          status: string
          strategy: string
          ticker: string
          tp_pct?: number
          version?: number
        }
        Update: {
          cutoff_n?: number
          entry_date?: string
          entry_price?: number
          exit_date?: string | null
          exit_price?: number | null
          holding_days?: number
          outcome_id?: string
          return_pct?: number | null
          sl_pct?: number
          status?: string
          strategy?: string
          ticker?: string
          tp_pct?: number
          version?: number
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
            referencedRelation: "candidate_supply_hints"
            referencedColumns: ["candidate_id", "attempt_run_id"]
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
      candidate_tags: {
        Row: {
          attempt_run_id: string
          candidate_id: string
          params_meta: Json
          signal_date: string
          status: string
          strategy: string
          tag_id: string
          tagged_at: string
        }
        Insert: {
          attempt_run_id: string
          candidate_id: string
          params_meta?: Json
          signal_date: string
          status?: string
          strategy: string
          tag_id?: string
          tagged_at?: string
        }
        Update: {
          attempt_run_id?: string
          candidate_id?: string
          params_meta?: Json
          signal_date?: string
          status?: string
          strategy?: string
          tag_id?: string
          tagged_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "candidate_tags_candidate_id_attempt_run_id_fkey"
            columns: ["candidate_id", "attempt_run_id"]
            isOneToOne: false
            referencedRelation: "candidate_supply_hints"
            referencedColumns: ["candidate_id", "attempt_run_id"]
          },
          {
            foreignKeyName: "candidate_tags_candidate_id_attempt_run_id_fkey"
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
      daily_ohlcv: {
        Row: {
          adjusted: boolean
          adjustment_version: number
          close: number
          high: number
          low: number
          open: number
          pricechk: number | null
          ticker: string
          trading_day: string
          volume: number
        }
        Insert: {
          adjusted?: boolean
          adjustment_version?: number
          close: number
          high: number
          low: number
          open: number
          pricechk?: number | null
          ticker: string
          trading_day: string
          volume: number
        }
        Update: {
          adjusted?: boolean
          adjustment_version?: number
          close?: number
          high?: number
          low?: number
          open?: number
          pricechk?: number | null
          ticker?: string
          trading_day?: string
          volume?: number
        }
        Relationships: []
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
      market_supply: {
        Row: {
          attempt_run_id: string
          collected_at: string
          foreign_net: number
          individual_net: number
          institution_net: number
          market: string
          program_net: number
          trading_day: string
        }
        Insert: {
          attempt_run_id: string
          collected_at?: string
          foreign_net: number
          individual_net: number
          institution_net: number
          market: string
          program_net: number
          trading_day: string
        }
        Update: {
          attempt_run_id?: string
          collected_at?: string
          foreign_net?: number
          individual_net?: number
          institution_net?: number
          market?: string
          program_net?: number
          trading_day?: string
        }
        Relationships: [
          {
            foreignKeyName: "market_supply_attempt_run_id_fkey"
            columns: ["attempt_run_id"]
            isOneToOne: false
            referencedRelation: "runs"
            referencedColumns: ["run_id"]
          },
        ]
      }
      outcome_events: {
        Row: {
          command_type: string
          created_at: string
          event_id: string
          logical_run_key: string
          payload: Json
          strategy: string
          ticker: string
        }
        Insert: {
          command_type: string
          created_at?: string
          event_id?: string
          logical_run_key: string
          payload?: Json
          strategy: string
          ticker: string
        }
        Update: {
          command_type?: string
          created_at?: string
          event_id?: string
          logical_run_key?: string
          payload?: Json
          strategy?: string
          ticker?: string
        }
        Relationships: [
          {
            foreignKeyName: "outcome_events_logical_run_key_fkey"
            columns: ["logical_run_key"]
            isOneToOne: false
            referencedRelation: "logical_runs"
            referencedColumns: ["logical_run_key"]
          },
        ]
      }
      outcome_observations: {
        Row: {
          close: number
          evaluation_trading_day: string
          high: number
          low: number
          outcome_id: string
          result_code: string
        }
        Insert: {
          close: number
          evaluation_trading_day: string
          high: number
          low: number
          outcome_id: string
          result_code: string
        }
        Update: {
          close?: number
          evaluation_trading_day?: string
          high?: number
          low?: number
          outcome_id?: string
          result_code?: string
        }
        Relationships: []
      }
      outcome_strategy_rule_history: {
        Row: {
          changed_at: string
          changed_by: string
          history_id: string
          new_cutoff_n: number | null
          new_sl_pct: number | null
          new_tp_pct: number | null
          operation: string
          previous_cutoff_n: number | null
          previous_sl_pct: number | null
          previous_tp_pct: number | null
          reason: string
          strategy: string
        }
        Insert: {
          changed_at?: string
          changed_by: string
          history_id?: string
          new_cutoff_n?: number | null
          new_sl_pct?: number | null
          new_tp_pct?: number | null
          operation: string
          previous_cutoff_n?: number | null
          previous_sl_pct?: number | null
          previous_tp_pct?: number | null
          reason: string
          strategy: string
        }
        Update: {
          changed_at?: string
          changed_by?: string
          history_id?: string
          new_cutoff_n?: number | null
          new_sl_pct?: number | null
          new_tp_pct?: number | null
          operation?: string
          previous_cutoff_n?: number | null
          previous_sl_pct?: number | null
          previous_tp_pct?: number | null
          reason?: string
          strategy?: string
        }
        Relationships: []
      }
      outcome_strategy_rules: {
        Row: {
          created_at: string
          cutoff_n: number
          sl_pct: number
          strategy: string
          tp_pct: number
        }
        Insert: {
          created_at?: string
          cutoff_n: number
          sl_pct: number
          strategy: string
          tp_pct: number
        }
        Update: {
          created_at?: string
          cutoff_n?: number
          sl_pct?: number
          strategy?: string
          tp_pct?: number
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
      supply_3day: {
        Row: {
          attempt_run_id: string
          candidate_id: string
          change_pct: number
          close: number
          collected_at: string
          foreign_net: number | null
          individual_net: number | null
          institution_net: number | null
          investor_net_status: string
          program_net: number | null
          slot: string
          trading_day: string
          volume: number
        }
        Insert: {
          attempt_run_id: string
          candidate_id: string
          change_pct: number
          close: number
          collected_at?: string
          foreign_net?: number | null
          individual_net?: number | null
          institution_net?: number | null
          investor_net_status: string
          program_net?: number | null
          slot: string
          trading_day: string
          volume: number
        }
        Update: {
          attempt_run_id?: string
          candidate_id?: string
          change_pct?: number
          close?: number
          collected_at?: string
          foreign_net?: number | null
          individual_net?: number | null
          institution_net?: number | null
          investor_net_status?: string
          program_net?: number | null
          slot?: string
          trading_day?: string
          volume?: number
        }
        Relationships: [
          {
            foreignKeyName: "supply_3day_candidate_id_attempt_run_id_fkey"
            columns: ["candidate_id", "attempt_run_id"]
            isOneToOne: false
            referencedRelation: "candidate_supply_hints"
            referencedColumns: ["candidate_id", "attempt_run_id"]
          },
          {
            foreignKeyName: "supply_3day_candidate_id_attempt_run_id_fkey"
            columns: ["candidate_id", "attempt_run_id"]
            isOneToOne: false
            referencedRelation: "candidates"
            referencedColumns: ["candidate_id", "attempt_run_id"]
          },
        ]
      }
      trading_calendar: {
        Row: {
          close_time: string | null
          is_open: boolean
          open_time: string | null
          trading_day: string
        }
        Insert: {
          close_time?: string | null
          is_open: boolean
          open_time?: string | null
          trading_day: string
        }
        Update: {
          close_time?: string | null
          is_open?: boolean
          open_time?: string | null
          trading_day?: string
        }
        Relationships: []
      }
    }
    Views: {
      bias_event_by_source_canonical: {
        Row: {
          backtest_universe_signal_count: number | null
          bias_event_id: string | null
          candidate_pop_signal_count: number | null
          contributing_candidate_count: number | null
          created_at: string | null
          diff_count: number | null
          intersection_count: number | null
          logical_run_key: string | null
          missed_opportunity_count: number | null
          source: string | null
          trading_day: string | null
        }
        Relationships: [
          {
            foreignKeyName: "bias_events_logical_run_key_fkey"
            columns: ["logical_run_key"]
            isOneToOne: false
            referencedRelation: "logical_runs"
            referencedColumns: ["logical_run_key"]
          },
        ]
      }
      bias_events_canonical: {
        Row: {
          bias_event_id: string | null
          calculation_meta: Json | null
          created_at: string | null
          logical_run_key: string | null
          trading_day: string | null
        }
        Relationships: [
          {
            foreignKeyName: "bias_events_logical_run_key_fkey"
            columns: ["logical_run_key"]
            isOneToOne: false
            referencedRelation: "logical_runs"
            referencedColumns: ["logical_run_key"]
          },
        ]
      }
      candidate_outcome_win_rate_pf: {
        Row: {
          delisted_count: number | null
          gross_loss: number | null
          gross_win: number | null
          losses: number | null
          open_count: number | null
          profit_factor: number | null
          suspended_count: number | null
          total_settled: number | null
          win_rate: number | null
          wins: number | null
        }
        Relationships: []
      }
      candidate_outcome_win_rate_pf_by_strategy_source: {
        Row: {
          delisted_count: number | null
          gross_loss: number | null
          gross_win: number | null
          losses: number | null
          open_count: number | null
          profit_factor: number | null
          source: string | null
          strategy: string | null
          suspended_count: number | null
          total_settled: number | null
          win_rate: number | null
          wins: number | null
        }
        Relationships: []
      }
      candidate_supply_hints: {
        Row: {
          attempt_run_id: string | null
          batch_kind: string | null
          candidate_id: string | null
          collected_at: string | null
          foreign_net: number | null
          hint_status: string | null
          individual_net: number | null
          institution_net: number | null
          investor_net_status: string | null
          program_net: number | null
          slot: string | null
          ticker: string | null
          trading_day: string | null
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
      append_bias_event: {
        Args: {
          p_calculation_meta: Json
          p_event_id: string
          p_fence_token: number
          p_lease_token: string
          p_rows: Json
          p_run_id: string
          p_status: string
        }
        Returns: Json
      }
      apply_outcome_correction: {
        Args: {
          p_expected_version: number
          p_logical_run_key: string
          p_new_cutoff_n?: number
          p_new_entry_price?: number
          p_new_exit_date?: string
          p_new_exit_price?: number
          p_new_holding_days?: number
          p_new_return_pct?: number
          p_new_status: string
          p_outcome_id: string
          p_reason: string
        }
        Returns: Json
      }
      claim_dispatch_outbox: {
        Args: { p_limit?: number; p_worker_lease_seconds?: number }
        Returns: Json
      }
      emit_open_command: {
        Args: {
          p_logical_run_key: string
          p_strategy: string
          p_ticker: string
        }
        Returns: Json
      }
      get_bias_population: {
        Args: { p_fence_token: number; p_lease_token: string; p_run_id: string }
        Returns: Json
      }
      get_candidate_evidence: { Args: { p_run_id: string }; Returns: Json }
      get_candidate_supply_hints: { Args: { p_run_id: string }; Returns: Json }
      get_dashboard_snapshot: { Args: never; Returns: Json }
      get_market_supply: { Args: { p_run_id: string }; Returns: Json }
      get_today_candidate_cards: { Args: { p_run_id: string }; Returns: Json }
      get_today_disappeared_candidates: {
        Args: { p_run_id: string }
        Returns: Json
      }
      heartbeat_attempt: {
        Args: {
          p_fence_token: number
          p_lease_seconds?: number
          p_lease_token: string
          p_run_id: string
        }
        Returns: Json
      }
      price_adjustment_gap_threshold: { Args: never; Returns: number }
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
      rebuild_outcome_projection: { Args: never; Returns: Json }
      reconcile_dispatch_outbox: { Args: never; Returns: Json }
      record_dispatch_receipt: {
        Args: { p_dispatch_request_id: string; p_run_id: string }
        Returns: Json
      }
      record_outcome_observation: {
        Args: {
          p_evaluation_trading_day: string
          p_outcome_id: string
          p_ticker: string
        }
        Returns: Json
      }
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
      set_outcome_strategy_rule: {
        Args: {
          p_changed_by: string
          p_cutoff_n: number
          p_reason: string
          p_sl_pct: number
          p_strategy: string
          p_tp_pct: number
        }
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
      sync_vanished_tags: { Args: { p_run_id: string }; Returns: Json }
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
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never) = never,
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
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
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
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
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
  EnumName extends (DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never) = never,
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
  CompositeTypeName extends (PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never) = never,
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
