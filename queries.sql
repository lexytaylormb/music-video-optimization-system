-- ============================================================================
-- PROJECT: Music Video Optimization & Performance Syndicate System
-- PURPOSE: Analytical Verification & Relational Data Validation Queries
-- ============================================================================

-- ----------------------------------------------------------------------------
-- ANALYTICAL QUERY 1: Content Genre Performance Metrics
-- ----------------------------------------------------------------------------
-- BUSINESS PURPOSE:
-- Evaluates audience engagement efficiency across distinct musical genres.
-- By calculating the interaction rate per view, media teams can see which 
-- genres drive active fan investment versus passive, muted consumption.
--
-- TECHNICAL HIGHLIGHTS:
-- Uses explicit INNER JOIN operations to connect normalized dimension maps 
-- back to the primary Fact table. Employs mathematically cast aggregates 
-- (* 1.0) to avoid integer division truncation and applies ROUND for 
-- pristine UI formatting.
-- ----------------------------------------------------------------------------

SELECT 
    a.primary_genre AS Content_Genre,
    COUNT(v.video_id) AS Total_Videos_Tracked,
    SUM(f.view_count) AS Aggregated_Views,
    ROUND(AVG(f.likes_count), 2) AS Average_Likes_Per_Video,
    ROUND((SUM(f.comment_count) * 1.0 / SUM(f.view_count)) * 100, 4) AS Audience_Interaction_Rate_Percentage
FROM Fact_Video_Metrics f
JOIN Dim_Videos v ON f.video_title = v.video_title
JOIN Dim_Artists a ON v.artist_name = a.artist_name
GROUP BY a.primary_genre
ORDER BY Aggregated_Views DESC;


-- ----------------------------------------------------------------------------
-- ANALYTICAL QUERY 2: Identifying High-Performer Strategic Channels
-- ----------------------------------------------------------------------------
-- BUSINESS PURPOSE:
-- Isolates premium, elite-tier media assets that have broken past major 
-- traffic milestones (1,000,000+ views) across syndication partners. 
-- This allows corporate executive leadership to quickly locate high-value 
-- content properties for ad-placement negotiations.
--
-- TECHNICAL HIGHLIGHTS:
-- Demonstrates proficiency using conditional filtering operators (WHERE), 
-- primary key/foreign key data extraction, and multi-column sorted outputs 
-- (ORDER BY) to handle high-density datasets efficiently.
-- ----------------------------------------------------------------------------

SELECT 
    v.video_title AS Asset_Title,
    v.artist_name AS Publisher,
    p.platform_name AS Active_Channel,
    f.view_count AS Total_Views,
    f.likes_count AS Core_Likes
FROM Fact_Video_Metrics f
JOIN Dim_Videos v ON f.video_title = v.video_title
JOIN Dim_Platforms p ON f.platform_id = p.platform_id
WHERE f.view_count > 1000000
ORDER BY f.view_count DESC;