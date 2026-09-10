-- Story 5.10 cutoff bias notice fixture. 모든 변경은 rollback으로 되돌린다.
begin;
-- ── parity fixture setup
insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct, cutoff_n, holding_days, tp_pct, sl_pct) values
('CTA001', 'A', '2098-05-01', 1000, 'TP', '2098-06-01', 1020, 2, 30, 2, 3, 3),
('CTA002', 'A', '2098-05-02', 1000, 'TP', '2098-06-02', 1020, 2, 30, 2, 3, 3),
('CTA003', 'A', '2098-05-03', 1000, 'TP', '2098-06-03', 1020, 2, 30, 2, 3, 3),
('CTA004', 'A', '2098-05-04', 1000, 'TP', '2098-06-04', 1020, 2, 30, 2, 3, 3),
('CTA005', 'A', '2098-05-05', 1000, 'TP', '2098-06-05', 1020, 2, 30, 2, 3, 3),
('CTA006', 'A', '2098-05-06', 1000, 'TP', '2098-06-06', 1020, 2, 30, 2, 3, 3),
('CTA007', 'A', '2098-05-07', 1000, 'TP', '2098-06-07', 1020, 2, 30, 2, 3, 3),
('CTA008', 'A', '2098-05-08', 1000, 'TP', '2098-06-08', 1020, 2, 30, 2, 3, 3),
('CTA009', 'A', '2098-05-09', 1000, 'TP', '2098-06-09', 1020, 2, 30, 2, 3, 3),
('CTA010', 'A', '2098-05-10', 1000, 'TP', '2098-06-10', 1020, 2, 30, 2, 3, 3),
('CTA011', 'A', '2098-05-11', 1000, 'TP', '2098-06-11', 1020, 2, 30, 2, 3, 3),
('CTA012', 'A', '2098-05-12', 1000, 'TP', '2098-06-12', 1020, 2, 30, 2, 3, 3),
('CTA013', 'A', '2098-05-13', 1000, 'TP', '2098-06-13', 1020, 2, 30, 2, 3, 3),
('CTA014', 'A', '2098-05-14', 1000, 'TP', '2098-06-14', 1020, 2, 30, 2, 3, 3),
('CTA015', 'A', '2098-05-15', 1000, 'SL', '2098-06-15', 980, -1, 30, 2, 3, 3),
('CTA016', 'A', '2098-05-16', 1000, 'SL', '2098-06-16', 980, -1, 30, 2, 3, 3),
('CTA017', 'A', '2098-05-17', 1000, 'SL', '2098-06-17', 980, -1, 30, 2, 3, 3),
('CTA018', 'A', '2098-05-18', 1000, 'SL', '2098-06-18', 980, -1, 30, 2, 3, 3),
('CTA019', 'A', '2098-05-19', 1000, 'SL', '2098-06-19', 980, -1, 30, 2, 3, 3),
('CTA020', 'A', '2098-05-20', 1000, 'SL', '2098-06-20', 980, -1, 30, 2, 3, 3),
('CTA021', 'A', '2098-05-21', 1000, 'SL', '2098-06-21', 980, -1, 30, 2, 3, 3),
('CTA022', 'A', '2098-05-22', 1000, 'SL', '2098-06-22', 980, -1, 30, 2, 3, 3),
('CTA023', 'A', '2098-05-23', 1000, 'SL', '2098-06-23', 980, -1, 30, 2, 3, 3),
('CTA024', 'A', '2098-05-24', 1000, 'SL', '2098-06-24', 980, -1, 30, 2, 3, 3),
('CTA025', 'A', '2098-05-25', 1000, 'SL', '2098-06-25', 980, -1, 30, 2, 3, 3),
('CTA026', 'A', '2098-05-26', 1000, 'SL', '2098-06-26', 980, -1, 30, 2, 3, 3),
('CTA027', 'A', '2098-05-27', 1000, 'SL', '2098-06-27', 980, -1, 30, 2, 3, 3),
('CTA028', 'A', '2098-05-28', 1000, 'SL', '2098-06-28', 980, -1, 30, 2, 3, 3),
('CTA029', 'A', '2098-05-01', 1000, 'SL', '2098-06-01', 980, -1, 30, 2, 3, 3),
('CTA030', 'A', '2098-05-02', 1000, 'TIMEOUT', '2098-06-02', 1005, 0.5, 30, 2, 3, 3),
('CTA031', 'A', '2098-05-03', 1000, 'OPEN', NULL, NULL, NULL, 30, 1, 3, 3),
('CTA032', 'A', '2098-05-04', 1000, 'SUSPENDED', NULL, NULL, NULL, 30, 0, 3, 3),
('CTA033', 'A', '2098-05-05', 1000, 'DELISTED', NULL, NULL, NULL, 30, 0, 3, 3),
('CTB001', 'B', '2098-05-01', 1000, 'TP', '2098-06-01', 1020, 2, 30, 2, 3, 3),
('CTB002', 'B', '2098-05-02', 1000, 'TP', '2098-06-02', 1020, 2, 30, 2, 3, 3),
('CTB003', 'B', '2098-05-03', 1000, 'TP', '2098-06-03', 1020, 2, 30, 2, 3, 3),
('CTB004', 'B', '2098-05-04', 1000, 'TP', '2098-06-04', 1020, 2, 30, 2, 3, 3),
('CTB005', 'B', '2098-05-05', 1000, 'TP', '2098-06-05', 1020, 2, 30, 2, 3, 3),
('CTB006', 'B', '2098-05-06', 1000, 'TP', '2098-06-06', 1020, 2, 30, 2, 3, 3),
('CTB007', 'B', '2098-05-07', 1000, 'TP', '2098-06-07', 1020, 2, 30, 2, 3, 3),
('CTB008', 'B', '2098-05-08', 1000, 'TP', '2098-06-08', 1020, 2, 30, 2, 3, 3),
('CTB009', 'B', '2098-05-09', 1000, 'TP', '2098-06-09', 1020, 2, 30, 2, 3, 3),
('CTB010', 'B', '2098-05-10', 1000, 'TP', '2098-06-10', 1020, 2, 30, 2, 3, 3),
('CTB011', 'B', '2098-05-11', 1000, 'TP', '2098-06-11', 1020, 2, 30, 2, 3, 3),
('CTB012', 'B', '2098-05-12', 1000, 'TP', '2098-06-12', 1020, 2, 30, 2, 3, 3),
('CTB013', 'B', '2098-05-13', 1000, 'TP', '2098-06-13', 1020, 2, 30, 2, 3, 3),
('CTB014', 'B', '2098-05-14', 1000, 'TP', '2098-06-14', 1020, 2, 30, 2, 3, 3),
('CTB015', 'B', '2098-05-15', 1000, 'SL', '2098-06-15', 980, -2, 30, 2, 3, 3),
('CTB016', 'B', '2098-05-16', 1000, 'SL', '2098-06-16', 980, -2, 30, 2, 3, 3),
('CTB017', 'B', '2098-05-17', 1000, 'SL', '2098-06-17', 980, -2, 30, 2, 3, 3),
('CTB018', 'B', '2098-05-18', 1000, 'SL', '2098-06-18', 980, -2, 30, 2, 3, 3),
('CTB019', 'B', '2098-05-19', 1000, 'SL', '2098-06-19', 980, -2, 30, 2, 3, 3),
('CTB020', 'B', '2098-05-20', 1000, 'SL', '2098-06-20', 980, -2, 30, 2, 3, 3),
('CTB021', 'B', '2098-05-21', 1000, 'SL', '2098-06-21', 980, -2, 30, 2, 3, 3),
('CTB022', 'B', '2098-05-22', 1000, 'SL', '2098-06-22', 980, -2, 30, 2, 3, 3),
('CTB023', 'B', '2098-05-23', 1000, 'SL', '2098-06-23', 980, -2, 30, 2, 3, 3),
('CTB024', 'B', '2098-05-24', 1000, 'SL', '2098-06-24', 980, -2, 30, 2, 3, 3),
('CTB025', 'B', '2098-05-25', 1000, 'SL', '2098-06-25', 980, -2, 30, 2, 3, 3),
('CTB026', 'B', '2098-05-26', 1000, 'SL', '2098-06-26', 980, -2, 30, 2, 3, 3),
('CTB027', 'B', '2098-05-27', 1000, 'SL', '2098-06-27', 980, -2, 30, 2, 3, 3),
('CTB028', 'B', '2098-05-28', 1000, 'SL', '2098-06-28', 980, -2, 30, 2, 3, 3),
('CTB029', 'B', '2098-05-01', 1000, 'SL', '2098-06-01', 980, -2, 30, 2, 3, 3),
('CTB030', 'B', '2098-05-02', 1000, 'TIMEOUT', '2098-06-02', 1005, 0.4, 30, 2, 3, 3),
('CTC001', 'C', '2098-05-01', 1000, 'TP', '2098-06-01', 1020, 2, 30, 2, 3, 3),
('CTC002', 'C', '2098-05-02', 1000, 'TP', '2098-06-02', 1020, 2, 30, 2, 3, 3),
('CTC003', 'C', '2098-05-03', 1000, 'TP', '2098-06-03', 1020, 2, 30, 2, 3, 3),
('CTC004', 'C', '2098-05-04', 1000, 'TP', '2098-06-04', 1020, 2, 30, 2, 3, 3),
('CTC005', 'C', '2098-05-05', 1000, 'TP', '2098-06-05', 1020, 2, 30, 2, 3, 3),
('CTC006', 'C', '2098-05-06', 1000, 'TP', '2098-06-06', 1020, 2, 30, 2, 3, 3),
('CTC007', 'C', '2098-05-07', 1000, 'TP', '2098-06-07', 1020, 2, 30, 2, 3, 3),
('CTC008', 'C', '2098-05-08', 1000, 'TP', '2098-06-08', 1020, 2, 30, 2, 3, 3),
('CTC009', 'C', '2098-05-09', 1000, 'TP', '2098-06-09', 1020, 2, 30, 2, 3, 3),
('CTC010', 'C', '2098-05-10', 1000, 'TP', '2098-06-10', 1020, 2, 30, 2, 3, 3),
('CTC011', 'C', '2098-05-11', 1000, 'TP', '2098-06-11', 1020, 2, 30, 2, 3, 3),
('CTC012', 'C', '2098-05-12', 1000, 'TP', '2098-06-12', 1020, 2, 30, 2, 3, 3),
('CTC013', 'C', '2098-05-13', 1000, 'TP', '2098-06-13', 1020, 2, 30, 2, 3, 3),
('CTC014', 'C', '2098-05-14', 1000, 'TP', '2098-06-14', 1020, 2, 30, 2, 3, 3),
('CTC015', 'C', '2098-05-15', 1000, 'SL', '2098-06-15', 980, -1, 30, 2, 3, 3),
('CTC016', 'C', '2098-05-16', 1000, 'SL', '2098-06-16', 980, -1, 30, 2, 3, 3),
('CTC017', 'C', '2098-05-17', 1000, 'SL', '2098-06-17', 980, -1, 30, 2, 3, 3),
('CTC018', 'C', '2098-05-18', 1000, 'SL', '2098-06-18', 980, -1, 30, 2, 3, 3),
('CTC019', 'C', '2098-05-19', 1000, 'SL', '2098-06-19', 980, -1, 30, 2, 3, 3),
('CTC020', 'C', '2098-05-20', 1000, 'SL', '2098-06-20', 980, -1, 30, 2, 3, 3),
('CTC021', 'C', '2098-05-21', 1000, 'SL', '2098-06-21', 980, -1, 30, 2, 3, 3),
('CTC022', 'C', '2098-05-22', 1000, 'SL', '2098-06-22', 980, -1, 30, 2, 3, 3),
('CTC023', 'C', '2098-05-23', 1000, 'SL', '2098-06-23', 980, -1, 30, 2, 3, 3),
('CTC024', 'C', '2098-05-24', 1000, 'SL', '2098-06-24', 980, -1, 30, 2, 3, 3),
('CTC025', 'C', '2098-05-25', 1000, 'SL', '2098-06-25', 980, -1, 30, 2, 3, 3),
('CTC026', 'C', '2098-05-26', 1000, 'SL', '2098-06-26', 980, -1, 30, 2, 3, 3),
('CTC027', 'C', '2098-05-27', 1000, 'SL', '2098-06-27', 980, -1, 30, 2, 3, 3),
('CTC028', 'C', '2098-05-28', 1000, 'SL', '2098-06-28', 980, -1, 30, 2, 3, 3),
('CTC029', 'C', '2098-05-01', 1000, 'SL', '2098-06-01', 980, -1, 30, 2, 3, 3),
('CTD001', 'D', '2098-05-01', 1000, 'TP', '2098-06-01', 1020, 2, 20, 2, 3, 5),
('CTD002', 'D', '2098-05-02', 1000, 'TP', '2098-06-02', 1020, 2, 20, 2, 3, 5),
('CTD003', 'D', '2098-05-03', 1000, 'TP', '2098-06-03', 1020, 2, 20, 2, 3, 5),
('CTD004', 'D', '2098-05-04', 1000, 'TP', '2098-06-04', 1020, 2, 20, 2, 3, 5),
('CTD005', 'D', '2098-05-05', 1000, 'TP', '2098-06-05', 1020, 2, 20, 2, 3, 5),
('CTD006', 'D', '2098-05-06', 1000, 'TP', '2098-06-06', 1020, 2, 20, 2, 3, 5),
('CTD007', 'D', '2098-05-07', 1000, 'TP', '2098-06-07', 1020, 2, 20, 2, 3, 5),
('CTD008', 'D', '2098-05-08', 1000, 'TP', '2098-06-08', 1020, 2, 20, 2, 3, 5),
('CTD009', 'D', '2098-05-09', 1000, 'TP', '2098-06-09', 1020, 2, 20, 2, 3, 5),
('CTD010', 'D', '2098-05-10', 1000, 'TP', '2098-06-10', 1020, 2, 20, 2, 3, 5),
('CTD011', 'D', '2098-05-11', 1000, 'TP', '2098-06-11', 1020, 2, 20, 2, 3, 5),
('CTD012', 'D', '2098-05-12', 1000, 'TP', '2098-06-12', 1020, 2, 20, 2, 3, 5),
('CTD013', 'D', '2098-05-13', 1000, 'TP', '2098-06-13', 1020, 2, 20, 2, 3, 5),
('CTD014', 'D', '2098-05-14', 1000, 'TP', '2098-06-14', 1020, 2, 20, 2, 3, 5),
('CTD015', 'D', '2098-05-15', 1000, 'TP', '2098-06-15', 1020, 2, 20, 2, 3, 5),
('CTD016', 'D', '2098-05-16', 1000, 'SL', '2098-06-16', 980, -1, 20, 2, 3, 5),
('CTD017', 'D', '2098-05-17', 1000, 'SL', '2098-06-17', 980, -1, 20, 2, 3, 5),
('CTD018', 'D', '2098-05-18', 1000, 'SL', '2098-06-18', 980, -1, 20, 2, 3, 5),
('CTD019', 'D', '2098-05-19', 1000, 'SL', '2098-06-19', 980, -1, 20, 2, 3, 5),
('CTD020', 'D', '2098-05-20', 1000, 'SL', '2098-06-20', 980, -1, 20, 2, 3, 5),
('CTD021', 'D', '2098-05-21', 1000, 'SL', '2098-06-21', 980, -1, 20, 2, 3, 5),
('CTD022', 'D', '2098-05-22', 1000, 'SL', '2098-06-22', 980, -1, 20, 2, 3, 5),
('CTD023', 'D', '2098-05-23', 1000, 'SL', '2098-06-23', 980, -1, 20, 2, 3, 5),
('CTD024', 'D', '2098-05-24', 1000, 'SL', '2098-06-24', 980, -1, 20, 2, 3, 5),
('CTD025', 'D', '2098-05-25', 1000, 'SL', '2098-06-25', 980, -1, 20, 2, 3, 5),
('CTD026', 'D', '2098-05-26', 1000, 'SL', '2098-06-26', 980, -1, 20, 2, 3, 5),
('CTD027', 'D', '2098-05-27', 1000, 'SL', '2098-06-27', 980, -1, 20, 2, 3, 5),
('CTD028', 'D', '2098-05-28', 1000, 'SL', '2098-06-28', 980, -1, 20, 2, 3, 5),
('CTD029', 'D', '2098-05-01', 1000, 'SL', '2098-06-01', 980, -1, 20, 2, 3, 5),
('CTD030', 'D', '2098-05-02', 1000, 'SL', '2098-06-02', 980, -1, 20, 2, 3, 5),
('CTE001', 'E', '2098-05-01', 1000, 'TP', '2098-06-01', 1020, 2, 30, 2, 2, 5),
('CTE002', 'E', '2098-05-02', 1000, 'TP', '2098-06-02', 1020, 2, 30, 2, 2, 5),
('CTE003', 'E', '2098-05-03', 1000, 'TP', '2098-06-03', 1020, 2, 30, 2, 2, 5),
('CTE004', 'E', '2098-05-04', 1000, 'TP', '2098-06-04', 1020, 2, 30, 2, 2, 5),
('CTE005', 'E', '2098-05-05', 1000, 'TP', '2098-06-05', 1020, 2, 30, 2, 2, 5),
('CTE006', 'E', '2098-05-06', 1000, 'TP', '2098-06-06', 1020, 2, 30, 2, 2, 5),
('CTE007', 'E', '2098-05-07', 1000, 'TP', '2098-06-07', 1020, 2, 30, 2, 2, 5),
('CTE008', 'E', '2098-05-08', 1000, 'TP', '2098-06-08', 1020, 2, 30, 2, 2, 5),
('CTE009', 'E', '2098-05-09', 1000, 'TP', '2098-06-09', 1020, 2, 30, 2, 2, 5),
('CTE010', 'E', '2098-05-10', 1000, 'TP', '2098-06-10', 1020, 2, 30, 2, 2, 5),
('CTE011', 'E', '2098-05-11', 1000, 'TP', '2098-06-11', 1020, 2, 30, 2, 2, 5),
('CTE012', 'E', '2098-05-12', 1000, 'TP', '2098-06-12', 1020, 2, 30, 2, 2, 5),
('CTE013', 'E', '2098-05-13', 1000, 'TP', '2098-06-13', 1020, 2, 30, 2, 2, 5),
('CTE014', 'E', '2098-05-14', 1000, 'TP', '2098-06-14', 1020, 2, 30, 2, 2, 5),
('CTE015', 'E', '2098-05-15', 1000, 'TP', '2098-06-15', 1020, 2, 30, 2, 2, 5),
('CTE016', 'E', '2098-05-16', 1000, 'SL', '2098-06-16', 980, -1, 30, 2, 2, 5),
('CTE017', 'E', '2098-05-17', 1000, 'SL', '2098-06-17', 980, -1, 30, 2, 2, 5),
('CTE018', 'E', '2098-05-18', 1000, 'SL', '2098-06-18', 980, -1, 30, 2, 2, 5),
('CTE019', 'E', '2098-05-19', 1000, 'SL', '2098-06-19', 980, -1, 30, 2, 2, 5),
('CTE020', 'E', '2098-05-20', 1000, 'SL', '2098-06-20', 980, -1, 30, 2, 2, 5),
('CTE021', 'E', '2098-05-21', 1000, 'SL', '2098-06-21', 980, -1, 30, 2, 2, 5),
('CTE022', 'E', '2098-05-22', 1000, 'SL', '2098-06-22', 980, -1, 30, 2, 2, 5),
('CTE023', 'E', '2098-05-23', 1000, 'SL', '2098-06-23', 980, -1, 30, 2, 2, 5),
('CTE024', 'E', '2098-05-24', 1000, 'SL', '2098-06-24', 980, -1, 30, 2, 2, 5),
('CTE025', 'E', '2098-05-25', 1000, 'SL', '2098-06-25', 980, -1, 30, 2, 2, 5),
('CTE026', 'E', '2098-05-26', 1000, 'SL', '2098-06-26', 980, -1, 30, 2, 2, 5),
('CTE027', 'E', '2098-05-27', 1000, 'SL', '2098-06-27', 980, -1, 30, 2, 2, 5),
('CTE028', 'E', '2098-05-28', 1000, 'SL', '2098-06-28', 980, -1, 30, 2, 2, 5),
('CTE029', 'E', '2098-05-01', 1000, 'SL', '2098-06-01', 980, -1, 30, 2, 2, 5),
('CTE030', 'E', '2098-05-02', 1000, 'SL', '2098-06-02', 980, -1, 30, 2, 2, 5),
('CTF001', 'F', '2098-05-01', 1000, 'TP', '2098-06-01', 1020, 2, 999999, 2, 3, 4),
('CTF002', 'F', '2098-05-02', 1000, 'TP', '2098-06-02', 1020, 2, 999999, 2, 3, 4),
('CTF003', 'F', '2098-05-03', 1000, 'TP', '2098-06-03', 1020, 2, 999999, 2, 3, 4),
('CTF004', 'F', '2098-05-04', 1000, 'TP', '2098-06-04', 1020, 2, 999999, 2, 3, 4),
('CTF005', 'F', '2098-05-05', 1000, 'TP', '2098-06-05', 1020, 2, 999999, 2, 3, 4),
('CTF006', 'F', '2098-05-06', 1000, 'TP', '2098-06-06', 1020, 2, 999999, 2, 3, 4),
('CTF007', 'F', '2098-05-07', 1000, 'TP', '2098-06-07', 1020, 2, 999999, 2, 3, 4),
('CTF008', 'F', '2098-05-08', 1000, 'TP', '2098-06-08', 1020, 2, 999999, 2, 3, 4),
('CTF009', 'F', '2098-05-09', 1000, 'TP', '2098-06-09', 1020, 2, 999999, 2, 3, 4),
('CTF010', 'F', '2098-05-10', 1000, 'TP', '2098-06-10', 1020, 2, 999999, 2, 3, 4),
('CTF011', 'F', '2098-05-11', 1000, 'TP', '2098-06-11', 1020, 2, 999999, 2, 3, 4),
('CTF012', 'F', '2098-05-12', 1000, 'TP', '2098-06-12', 1020, 2, 999999, 2, 3, 4),
('CTF013', 'F', '2098-05-13', 1000, 'TP', '2098-06-13', 1020, 2, 999999, 2, 3, 4),
('CTF014', 'F', '2098-05-14', 1000, 'TP', '2098-06-14', 1020, 2, 999999, 2, 3, 4),
('CTF015', 'F', '2098-05-15', 1000, 'TP', '2098-06-15', 1020, 2, 999999, 2, 3, 4),
('CTF016', 'F', '2098-05-16', 1000, 'SL', '2098-06-16', 980, -1, 999999, 2, 3, 4),
('CTF017', 'F', '2098-05-17', 1000, 'SL', '2098-06-17', 980, -1, 999999, 2, 3, 4),
('CTF018', 'F', '2098-05-18', 1000, 'SL', '2098-06-18', 980, -1, 999999, 2, 3, 4),
('CTF019', 'F', '2098-05-19', 1000, 'SL', '2098-06-19', 980, -1, 999999, 2, 3, 4),
('CTF020', 'F', '2098-05-20', 1000, 'SL', '2098-06-20', 980, -1, 999999, 2, 3, 4),
('CTF021', 'F', '2098-05-21', 1000, 'SL', '2098-06-21', 980, -1, 999999, 2, 3, 4),
('CTF022', 'F', '2098-05-22', 1000, 'SL', '2098-06-22', 980, -1, 999999, 2, 3, 4),
('CTF023', 'F', '2098-05-23', 1000, 'SL', '2098-06-23', 980, -1, 999999, 2, 3, 4),
('CTF024', 'F', '2098-05-24', 1000, 'SL', '2098-06-24', 980, -1, 999999, 2, 3, 4),
('CTF025', 'F', '2098-05-25', 1000, 'SL', '2098-06-25', 980, -1, 999999, 2, 3, 4),
('CTF026', 'F', '2098-05-26', 1000, 'SL', '2098-06-26', 980, -1, 999999, 2, 3, 4),
('CTF027', 'F', '2098-05-27', 1000, 'SL', '2098-06-27', 980, -1, 999999, 2, 3, 4),
('CTF028', 'F', '2098-05-28', 1000, 'SL', '2098-06-28', 980, -1, 999999, 2, 3, 4),
('CTF029', 'F', '2098-05-01', 1000, 'SL', '2098-06-01', 980, -1, 999999, 2, 3, 4),
('CTF030', 'F', '2098-05-02', 1000, 'SL', '2098-06-02', 980, -1, 999999, 2, 3, 4);

create temp table cutoff_bias_expected (
  strategy text,
  total_settled integer,
  wins integer,
  losses integer,
  open_count integer,
  suspended_count integer,
  delisted_count integer,
  gross_win numeric,
  gross_loss numeric,
  win_rate numeric,
  profit_factor numeric,
  sample_gate_min_required integer,
  sample_gate_passed boolean,
  sample_gate_label text,
  ci_lower numeric,
  ci_upper numeric,
  expected_win_rate numeric,
  expected_in_ci boolean,
  expected_profit_factor numeric,
  win_rate_threshold_pp numeric,
  profit_factor_threshold_ratio numeric,
  win_rate_threshold_breached boolean,
  profit_factor_threshold_breached boolean,
  threshold_warning boolean,
  timeout_count integer,
  cutoff_bias_sample_size integer,
  cutoff_bias_timeout_rate numeric,
  cutoff_bias_profit_factor_delta numeric,
  cutoff_bias_label text
);
insert into cutoff_bias_expected values
('A', 30, 15, 15, 1, 1, 1, 28.5, 15, 0.5, 1.9, 30, TRUE, NULL, 0.3315, 0.6685, 0.6871, FALSE, 2.054, 0.1, 0.25, TRUE, FALSE, TRUE, 1, 30, 0, 0, 'TIMEOUT 0% / PF차 ±0'),
('B', 30, 15, 15, 0, 0, 0, 28.4, 30, 0.5, 0.9467, 30, TRUE, NULL, 0.3315, 0.6685, 0.6895, FALSE, 2.077, 0.1, 0.25, TRUE, TRUE, TRUE, 1, 30, 0.0037, 0.0125, 'TIMEOUT 0.37% / PF차 +0.0125'),
('C', 29, 14, 15, 0, 0, 0, 28, 15, NULL, NULL, 30, FALSE, '표본 부족 (29/30)', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 30, 0, 0, 'TIMEOUT 0% / PF차 ±0'),
('D', 30, 15, 15, 0, 0, 0, 30, 15, 0.5, 2, 30, TRUE, NULL, 0.3315, 0.6685, NULL, NULL, NULL, 0.1, 0.25, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL),
('E', 30, 15, 15, 0, 0, 0, 30, 15, 0.5, 2, 30, TRUE, NULL, 0.3315, 0.6685, NULL, NULL, NULL, 0.1, 0.25, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL),
('F', 30, 15, 15, 0, 0, 0, 30, 15, 0.5, 2, 30, TRUE, NULL, 0.3315, 0.6685, NULL, NULL, NULL, 0.1, 0.25, NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL),
(NULL, 179, 89, 90, 1, 1, 1, 174.9, 105, 0.4972, 1.6657, 30, TRUE, NULL, 0.4248, 0.5697, NULL, NULL, NULL, 0.1, 0.25, NULL, NULL, NULL, 2, NULL, NULL, NULL, NULL);

-- ── sql-only assertions
do $$
declare diff_count integer;
begin
  if (select count(*) from cutoff_bias_expected) <> 7 then
    raise exception 'story 5-10: expected row cardinality drift';
  end if;
  if (select count(*) from public.candidate_outcome_cutoff_bias_notice) <> 7 then
    raise exception 'story 5-10: view row cardinality drift';
  end if;
  select count(*) into diff_count from (
    (select * from public.candidate_outcome_cutoff_bias_notice except select * from cutoff_bias_expected)
    union all
    (select * from cutoff_bias_expected except select * from public.candidate_outcome_cutoff_bias_notice)
  ) differences;
  if diff_count <> 0 then
    raise exception 'story 5-10 cutoff bias notice mismatch: % differing rows', diff_count;
  end if;
end $$;

do $$
declare a_row record; b_row record; c_row record; d_row record; rollup_row record;
begin
  select * into a_row from public.candidate_outcome_cutoff_bias_notice where strategy = 'A';
  select * into b_row from public.candidate_outcome_cutoff_bias_notice where strategy = 'B';
  select * into c_row from public.candidate_outcome_cutoff_bias_notice where strategy = 'C';
  select * into d_row from public.candidate_outcome_cutoff_bias_notice where strategy = 'D';
  select * into rollup_row from public.candidate_outcome_cutoff_bias_notice where strategy is null;

  if a_row.timeout_count <> 1 or a_row.cutoff_bias_sample_size <> 30
     or a_row.cutoff_bias_timeout_rate <> 0.0000
     or a_row.cutoff_bias_profit_factor_delta <> 0.0000
     or a_row.cutoff_bias_label <> 'TIMEOUT 0% / PF차 ±0' then
    raise exception 'story 5-10: A notice contract mismatch';
  end if;
  if b_row.timeout_count <> 1
     or b_row.cutoff_bias_timeout_rate <> 0.0037
     or b_row.cutoff_bias_profit_factor_delta <> 0.0125
     or b_row.cutoff_bias_label <> 'TIMEOUT 0.37% / PF차 +0.0125' then
    raise exception 'story 5-10: B notice contract mismatch';
  end if;
  if c_row.timeout_count <> 0 or c_row.sample_gate_passed
     or c_row.cutoff_bias_sample_size <> 30
     or c_row.cutoff_bias_label <> 'TIMEOUT 0% / PF차 ±0' then
    raise exception 'story 5-10: C gate-independent notice mismatch';
  end if;
  if d_row.timeout_count <> 0
     or d_row.cutoff_bias_sample_size is not null
     or d_row.cutoff_bias_timeout_rate is not null
     or d_row.cutoff_bias_profit_factor_delta is not null
     or d_row.cutoff_bias_label is not null then
    raise exception 'story 5-10: D must not receive an invented baseline';
  end if;
  if rollup_row.timeout_count <> 2
     or rollup_row.cutoff_bias_sample_size is not null
     or rollup_row.cutoff_bias_label is not null then
    raise exception 'story 5-10: rollup notice contract mismatch';
  end if;
end $$;

do $$
begin
  if has_table_privilege('anon', 'public.candidate_outcome_cutoff_bias_notice', 'select') then
    raise exception 'story 5-10: anon direct SELECT must be denied';
  end if;
  if has_table_privilege('authenticated', 'public.candidate_outcome_cutoff_bias_notice', 'select') then
    raise exception 'story 5-10: authenticated direct SELECT must be denied';
  end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public'
      and table_name = 'candidate_outcome_cutoff_bias_notice'
      and column_name = 'cutoff_bias_label'
  ) then
    raise exception 'story 5-10: cutoff bias label column missing from catalog';
  end if;
  if not has_table_privilege('service_role', 'public.candidate_outcome_cutoff_bias_notice', 'select') then
    raise exception 'story 5-10: service_role read privilege is missing';
  end if;
  if (select count(*) from information_schema.columns
      where table_schema = 'public'
        and table_name = 'candidate_outcome_cutoff_bias_notice') <> 29 then
    raise exception 'story 5-10: view column cardinality drift';
  end if;
  if (select array_agg(column_name order by ordinal_position)
      from information_schema.columns
      where table_schema = 'public'
        and table_name = 'candidate_outcome_cutoff_bias_notice') <> array[
        'strategy', 'total_settled', 'wins', 'losses', 'open_count',
        'suspended_count', 'delisted_count', 'gross_win', 'gross_loss',
        'win_rate', 'profit_factor', 'sample_gate_min_required',
        'sample_gate_passed', 'sample_gate_label', 'ci_lower', 'ci_upper',
        'expected_win_rate', 'expected_in_ci', 'expected_profit_factor',
        'win_rate_threshold_pp', 'profit_factor_threshold_ratio',
        'win_rate_threshold_breached', 'profit_factor_threshold_breached',
        'threshold_warning', 'timeout_count', 'cutoff_bias_sample_size',
        'cutoff_bias_timeout_rate', 'cutoff_bias_profit_factor_delta',
        'cutoff_bias_label'
      ]::text[] then
    raise exception 'story 5-10: view column name/order drift';
  end if;
end $$;

savepoint empty_candidate_outcome;
delete from public.candidate_outcome;
do $$
declare empty_row record;
begin
  select * into empty_row
  from public.candidate_outcome_cutoff_bias_notice
  where strategy is null;
  if not found or empty_row.timeout_count <> 0
     or empty_row.cutoff_bias_sample_size is not null
     or empty_row.cutoff_bias_label is not null then
    raise exception 'story 5-10: empty candidate_outcome state mismatch';
  end if;
end $$;
rollback to savepoint empty_candidate_outcome;

rollback;

select
  'pass'::text as fixture_status,
  'story 5-10 cutoff bias notice'::text as fixture_name,
  7::integer as asserted_view_rows;
