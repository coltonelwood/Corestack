-- ABF Seed Data
-- Migration 002: Realistic sample data for development and demos.
--
-- Uses fixed UUIDs so foreign keys and references are deterministic.
-- Safe to re-run: uses ON CONFLICT DO NOTHING where applicable.

-- ============================================================
-- Businesses
-- ============================================================

insert into businesses (id, name, domain, description, status, created_at) values
  ('a1b2c3d4-0001-4000-8000-000000000001', 'NovaBright Skincare',    'novabrightskin.com',     'DTC premium skincare brand',             'active',  '2024-09-15T00:00:00Z'),
  ('a1b2c3d4-0001-4000-8000-000000000002', 'PeakFit Supplements',    'peakfitsupps.com',       'Performance nutrition and supplements',   'active',  '2024-10-02T00:00:00Z'),
  ('a1b2c3d4-0001-4000-8000-000000000003', 'UrbanNest Home',         'urbannesthome.com',      'Modern home decor and furniture',         'active',  '2024-10-18T00:00:00Z'),
  ('a1b2c3d4-0001-4000-8000-000000000004', 'CloudPaw Pet Co',        'cloudpawpets.com',       'Premium pet products marketplace',        'setup',   '2025-01-08T00:00:00Z'),
  ('a1b2c3d4-0001-4000-8000-000000000005', 'MindFlow Journals',      'mindflowjournals.com',   'Guided journals and planners',            'active',  '2024-11-05T00:00:00Z'),
  ('a1b2c3d4-0001-4000-8000-000000000006', 'SolarEdge Tech',         'solaredgetech.io',       'B2B solar panel technology',              'paused',  '2024-08-22T00:00:00Z');

-- ============================================================
-- Products
-- ============================================================

insert into products (id, business_id, name, description, category, price_cents, cost_cents, status, inventory, sales_count, created_at) values
  ('b1b2c3d4-0002-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000001', 'Vitamin C Radiance Serum',   'Brightening serum with 15% vitamin C',          'Serums',       4200, 840,  'active',  1240, 3842, '2024-09-20T00:00:00Z'),
  ('b1b2c3d4-0002-4000-8000-000000000002', 'a1b2c3d4-0001-4000-8000-000000000001', 'Hyaluronic Moisture Cream',  'Deep hydration with hyaluronic acid',            'Moisturizers', 3800, 720,  'active',  890,  2716, '2024-09-20T00:00:00Z'),
  ('b1b2c3d4-0002-4000-8000-000000000003', 'a1b2c3d4-0001-4000-8000-000000000001', 'Retinol Night Repair',       'Anti-aging overnight treatment',                 'Treatments',   5600, 1100, 'active',  560,  1890, '2024-10-15T00:00:00Z'),
  ('b1b2c3d4-0002-4000-8000-000000000004', 'a1b2c3d4-0002-4000-8000-000000000002', 'Whey Protein Isolate',       '100% grass-fed whey, 30g protein per serving',   'Protein',      5400, 1200, 'active',  2100, 1893, '2024-10-05T00:00:00Z'),
  ('b1b2c3d4-0002-4000-8000-000000000005', 'a1b2c3d4-0002-4000-8000-000000000002', 'Pre-Workout Ignite',         'High-stim pre-workout with beta-alanine',        'Pre-Workout',  3600, 680,  'active',  1560, 2104, '2024-10-10T00:00:00Z'),
  ('b1b2c3d4-0002-4000-8000-000000000006', 'a1b2c3d4-0003-4000-8000-000000000003', 'Minimalist Desk Lamp',       'Adjustable LED desk lamp, matte black',          'Lighting',     8900, 2200, 'active',  340,  876,  '2024-10-22T00:00:00Z'),
  ('b1b2c3d4-0002-4000-8000-000000000007', 'a1b2c3d4-0003-4000-8000-000000000003', 'Bamboo Shelf System',        'Modular bamboo shelving, 3-tier',                'Furniture',   14900, 4800, 'draft',   120,  0,    '2025-01-03T00:00:00Z'),
  ('b1b2c3d4-0002-4000-8000-000000000008', 'a1b2c3d4-0005-4000-8000-000000000005', 'Daily Gratitude Journal',    'Guided gratitude journal with prompts',          'Journals',     2800, 420,  'active',  3200, 4210, '2024-11-10T00:00:00Z'),
  ('b1b2c3d4-0002-4000-8000-000000000009', 'a1b2c3d4-0005-4000-8000-000000000005', 'Goal Planner Pro',           '90-day goal-setting planner',                    'Planners',     3400, 560,  'active',  1800, 1567, '2024-12-01T00:00:00Z');

-- ============================================================
-- Campaigns
-- ============================================================

insert into campaigns (id, business_id, product_id, name, channel, status, budget_cents, spent_cents, impressions, clicks, conversions, start_date, end_date, created_at) values
  ('c1b2c3d4-0003-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000001', null,                                      'Spring Glow Collection Launch',   'meta',     'active',    1500000, 1124000, 842000,  23800, 1420, '2025-01-10', '2025-02-10', '2025-01-09T00:00:00Z'),
  ('c1b2c3d4-0003-4000-8000-000000000002', 'a1b2c3d4-0001-4000-8000-000000000001', 'b1b2c3d4-0002-4000-8000-000000000003',     'Retinol Night Cream - Search',    'google',   'active',     800000,  567000, 320000,  14200,  890, '2025-01-05', '2025-03-05', '2025-01-04T00:00:00Z'),
  ('c1b2c3d4-0003-4000-8000-000000000003', 'a1b2c3d4-0002-4000-8000-000000000002', null,                                      'New Year Fitness Push',            'tiktok',   'completed', 1200000, 1200000, 1240000, 45600, 2340, '2024-12-26', '2025-01-15', '2024-12-25T00:00:00Z'),
  ('c1b2c3d4-0003-4000-8000-000000000004', 'a1b2c3d4-0002-4000-8000-000000000002', 'b1b2c3d4-0002-4000-8000-000000000004',     'Protein Launch Email Series',      'email',    'active',     200000,   80000,  48000,   6200,  420, '2025-01-12', '2025-02-12', '2025-01-11T00:00:00Z'),
  ('c1b2c3d4-0003-4000-8000-000000000005', 'a1b2c3d4-0003-4000-8000-000000000003', 'b1b2c3d4-0002-4000-8000-000000000006',     'Home Office Essentials',           'meta',     'active',    1000000,  780000, 560000,  18400,  960, '2025-01-08', '2025-02-08', '2025-01-07T00:00:00Z'),
  ('c1b2c3d4-0003-4000-8000-000000000006', 'a1b2c3d4-0005-4000-8000-000000000005', null,                                      'LinkedIn Thought Leadership',      'linkedin', 'active',     500000,  320000, 180000,   8400,  340, '2025-01-15', '2025-03-15', '2025-01-14T00:00:00Z');

-- ============================================================
-- Tasks
-- ============================================================

insert into tasks (id, business_id, title, description, status, priority, assigned_agent, payload, result, created_at, completed_at) values
  ('d1b2c3d4-0004-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000001',
   'Generate product descriptions for Spring Collection',
   'Create SEO-optimized descriptions for 12 new products',
   'completed', 'high', 'Content Writer',
   '{"product_count": 12, "style": "premium", "seo": true}',
   '{"descriptions_generated": 12, "avg_word_count": 180}',
   '2025-01-12T09:00:00Z', '2025-01-12T09:34:00Z'),

  ('d1b2c3d4-0004-4000-8000-000000000002', 'a1b2c3d4-0001-4000-8000-000000000001',
   'Optimize Meta ad creative for CTR',
   'A/B test 5 headline variants and select the top performer',
   'in_progress', 'high', 'Ads Manager',
   '{"variants": 5, "platform": "meta", "metric": "ctr"}',
   null,
   '2025-01-13T08:00:00Z', null),

  ('d1b2c3d4-0004-4000-8000-000000000003', 'a1b2c3d4-0002-4000-8000-000000000002',
   'Competitor pricing analysis',
   'Scrape and analyze pricing for top 20 competitors',
   'completed', 'medium', 'Research Analyst',
   '{"competitor_count": 20, "categories": ["protein", "pre-workout"]}',
   '{"avg_price_diff": -8.5, "underpriced_skus": 3}',
   '2025-01-11T14:00:00Z', '2025-01-11T14:48:00Z'),

  ('d1b2c3d4-0004-4000-8000-000000000004', 'a1b2c3d4-0002-4000-8000-000000000002',
   'Set up TikTok pixel tracking',
   'Install and verify conversion tracking on storefront',
   'pending', 'critical', 'Ads Manager',
   '{"platform": "tiktok", "pixel_type": "standard"}',
   null,
   '2025-01-13T10:00:00Z', null),

  ('d1b2c3d4-0004-4000-8000-000000000005', 'a1b2c3d4-0003-4000-8000-000000000003',
   'Weekly performance report',
   'Compile KPI dashboard for all active campaigns',
   'in_progress', 'medium', 'Analytics Agent',
   '{"report_type": "weekly", "include_forecasts": true}',
   null,
   '2025-01-13T06:00:00Z', null),

  ('d1b2c3d4-0004-4000-8000-000000000006', 'a1b2c3d4-0005-4000-8000-000000000005',
   'Email welcome sequence copy',
   'Write 5-email onboarding sequence for new subscribers',
   'pending', 'medium', 'Content Writer',
   '{"email_count": 5, "tone": "warm", "cta_focus": "purchase"}',
   null,
   '2025-01-13T11:00:00Z', null),

  ('d1b2c3d4-0004-4000-8000-000000000007', 'a1b2c3d4-0001-4000-8000-000000000001',
   'Restock inventory forecast',
   'Predict restock needs for next 30 days based on sales velocity',
   'completed', 'high', 'Operations Agent',
   '{"horizon_days": 30, "method": "weighted_moving_avg"}',
   '{"items_to_restock": 4, "estimated_cost_cents": 1840000}',
   '2025-01-12T16:00:00Z', '2025-01-12T16:22:00Z'),

  ('d1b2c3d4-0004-4000-8000-000000000008', 'a1b2c3d4-0006-4000-8000-000000000006',
   'Landing page SEO audit',
   'Audit top 5 landing pages and suggest improvements',
   'failed', 'low', 'Research Analyst',
   '{"page_count": 5, "audit_depth": "full"}',
   '{"error": "Unable to access 3 of 5 pages — site is paused"}',
   '2025-01-10T13:00:00Z', '2025-01-10T13:15:00Z');

-- ============================================================
-- Agent Runs
-- ============================================================

insert into agent_runs (id, task_id, business_id, agent_name, agent_type, status, duration_ms, tokens_used, cost_cents, input_payload, output_payload, error_message, started_at, completed_at) values
  ('e1b2c3d4-0005-4000-8000-000000000001',
   'd1b2c3d4-0004-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000001',
   'Content Writer', 'content', 'completed', 204000, 18420, 28,
   '{"task": "product_descriptions", "count": 12}',
   '{"descriptions_generated": 12}',
   null,
   '2025-01-12T09:00:00Z', '2025-01-12T09:03:24Z'),

  ('e1b2c3d4-0005-4000-8000-000000000002',
   'd1b2c3d4-0004-4000-8000-000000000002', 'a1b2c3d4-0001-4000-8000-000000000001',
   'Ads Manager', 'ads', 'running', null, 4200, 6,
   '{"task": "ab_test", "platform": "meta", "variants": 5}',
   null, null,
   '2025-01-13T08:00:00Z', null),

  ('e1b2c3d4-0005-4000-8000-000000000003',
   'd1b2c3d4-0004-4000-8000-000000000003', 'a1b2c3d4-0002-4000-8000-000000000002',
   'Research Analyst', 'research', 'completed', 2880000, 34600, 52,
   '{"task": "competitor_pricing", "brands": 20}',
   '{"report_url": "/reports/pricing-2025-01.pdf"}',
   null,
   '2025-01-11T14:00:00Z', '2025-01-11T14:48:00Z'),

  ('e1b2c3d4-0005-4000-8000-000000000004',
   'd1b2c3d4-0004-4000-8000-000000000005', 'a1b2c3d4-0003-4000-8000-000000000003',
   'Analytics Agent', 'analytics', 'running', null, 8900, 13,
   '{"task": "weekly_kpi", "include_forecasts": true}',
   null, null,
   '2025-01-13T06:00:00Z', null),

  ('e1b2c3d4-0005-4000-8000-000000000005',
   'd1b2c3d4-0004-4000-8000-000000000007', 'a1b2c3d4-0001-4000-8000-000000000001',
   'Operations Agent', 'operations', 'completed', 1320000, 12800, 19,
   '{"task": "restock_forecast", "horizon_days": 30}',
   '{"items_to_restock": 4}',
   null,
   '2025-01-12T16:00:00Z', '2025-01-12T16:22:00Z'),

  ('e1b2c3d4-0005-4000-8000-000000000006',
   null, 'a1b2c3d4-0001-4000-8000-000000000001',
   'Outreach Agent', 'outreach', 'queued', null, 0, 0,
   '{"task": "influencer_outreach", "campaign": "spring"}',
   null, null,
   '2025-01-13T12:00:00Z', null),

  ('e1b2c3d4-0005-4000-8000-000000000007',
   'd1b2c3d4-0004-4000-8000-000000000008', 'a1b2c3d4-0006-4000-8000-000000000006',
   'Content Writer', 'content', 'failed', 900000, 6200, 9,
   '{"task": "seo_audit", "pages": 5}',
   null,
   'Unable to access 3 of 5 pages — site is paused',
   '2025-01-10T13:00:00Z', '2025-01-10T13:15:00Z');

-- ============================================================
-- Approvals
-- ============================================================

insert into approvals (id, business_id, type, title, description, status, requested_by, reviewed_by, amount_cents, payload, created_at, reviewed_at) values
  ('f1b2c3d4-0006-4000-8000-000000000001', 'a1b2c3d4-0002-4000-8000-000000000002',
   'campaign_launch',
   'Launch TikTok Retargeting Campaign',
   'Retarget website visitors with dynamic product ads on TikTok',
   'pending', 'Ads Manager', null, 850000,
   '{"platform": "tiktok", "audience": "retargeting"}',
   '2025-01-13T09:30:00Z', null),

  ('f1b2c3d4-0006-4000-8000-000000000002', 'a1b2c3d4-0001-4000-8000-000000000001',
   'budget_increase',
   'Increase Meta budget for Spring Glow',
   'Campaign is hitting 4.2x ROAS — requesting 50% budget increase',
   'pending', 'Ads Manager', null, 750000,
   '{"current_roas": 4.2, "increase_pct": 50}',
   '2025-01-13T08:15:00Z', null),

  ('f1b2c3d4-0006-4000-8000-000000000003', 'a1b2c3d4-0005-4000-8000-000000000005',
   'content_publish',
   'Publish blog post: 10 Morning Routine Tips',
   'SEO article targeting ''morning routine'' keywords. 2,400 words.',
   'pending', 'Content Writer', null, null,
   '{"word_count": 2400, "target_keyword": "morning routine"}',
   '2025-01-13T07:00:00Z', null),

  ('f1b2c3d4-0006-4000-8000-000000000004', 'a1b2c3d4-0003-4000-8000-000000000003',
   'product_listing',
   'List Bamboo Shelf System on storefront',
   'New product ready for listing with AI-generated descriptions and images',
   'approved', 'Operations Agent', 'admin', null,
   '{"product_id": "b1b2c3d4-0002-4000-8000-000000000007"}',
   '2025-01-12T15:00:00Z', '2025-01-12T16:30:00Z'),

  ('f1b2c3d4-0006-4000-8000-000000000005', 'a1b2c3d4-0002-4000-8000-000000000002',
   'price_change',
   'Reduce Pre-Workout Ignite price by 15%',
   'Competitive analysis shows we are overpriced vs. top 3 competitors',
   'rejected', 'Research Analyst', 'admin', null,
   '{"product_id": "b1b2c3d4-0002-4000-8000-000000000005", "reduction_pct": 15}',
   '2025-01-11T14:50:00Z', '2025-01-11T17:00:00Z'),

  ('f1b2c3d4-0006-4000-8000-000000000006', 'a1b2c3d4-0006-4000-8000-000000000006',
   'campaign_launch',
   'Launch LinkedIn awareness campaign',
   'Target B2B decision makers with thought leadership content',
   'approved', 'Ads Manager', 'admin', 500000,
   '{"platform": "linkedin", "audience": "b2b_decision_makers"}',
   '2025-01-10T10:00:00Z', '2025-01-10T12:00:00Z');

-- ============================================================
-- Audit Logs (sample entries)
-- ============================================================

insert into audit_logs (id, business_id, actor, action, entity_type, entity_id, diff, created_at) values
  ('aa00c3d4-0007-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000001',
   'system', 'create', 'business', 'a1b2c3d4-0001-4000-8000-000000000001',
   '{"name": "NovaBright Skincare"}',
   '2024-09-15T00:00:00Z'),

  ('aa00c3d4-0007-4000-8000-000000000002', 'a1b2c3d4-0001-4000-8000-000000000001',
   'Ads Manager', 'create', 'campaign', 'c1b2c3d4-0003-4000-8000-000000000001',
   '{"name": "Spring Glow Collection Launch", "budget_cents": 1500000}',
   '2025-01-09T00:00:00Z'),

  ('aa00c3d4-0007-4000-8000-000000000003', 'a1b2c3d4-0003-4000-8000-000000000003',
   'admin', 'approve', 'approval', 'f1b2c3d4-0006-4000-8000-000000000004',
   '{"status": {"from": "pending", "to": "approved"}}',
   '2025-01-12T16:30:00Z'),

  ('aa00c3d4-0007-4000-8000-000000000004', 'a1b2c3d4-0002-4000-8000-000000000002',
   'admin', 'reject', 'approval', 'f1b2c3d4-0006-4000-8000-000000000005',
   '{"status": {"from": "pending", "to": "rejected"}}',
   '2025-01-11T17:00:00Z');

-- ============================================================
-- Memory (sample agent memory entries)
-- ============================================================

insert into memory (id, business_id, agent_name, namespace, key, value, created_at) values
  ('bb00c3d4-0008-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000001',
   'Content Writer', 'brand_voice', 'tone',
   '{"style": "premium", "adjectives": ["radiant", "luminous", "transformative"], "avoid": ["cheap", "basic"]}',
   '2024-09-20T00:00:00Z'),

  ('bb00c3d4-0008-4000-8000-000000000002', 'a1b2c3d4-0002-4000-8000-000000000002',
   'Research Analyst', 'market_data', 'competitor_landscape',
   '{"top_competitors": ["BrandX", "FitPro", "NutriMax"], "avg_price_protein_cents": 4800, "last_updated": "2025-01-11"}',
   '2025-01-11T14:48:00Z'),

  ('bb00c3d4-0008-4000-8000-000000000003', 'a1b2c3d4-0001-4000-8000-000000000001',
   'Ads Manager', 'performance', 'meta_benchmarks',
   '{"avg_ctr": 2.8, "avg_cpc_cents": 47, "avg_roas": 4.2, "best_audience": "women_25_44"}',
   '2025-01-13T08:00:00Z');
