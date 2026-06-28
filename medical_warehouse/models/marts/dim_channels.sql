with base as (
    select *
    from {{ ref('stg_telegram_messages') }}
),

channel_stats as (
    select
        channel_name,

        min(message_date) as first_post_date,
        max(message_date) as last_post_date,
        count(*) as total_posts,
        avg(views) as avg_views

    from base
    group by channel_name
)

select
    {{ dbt_utils.generate_surrogate_key(['channel_name']) }} as channel_key,
    channel_name,
    first_post_date,
    last_post_date,
    total_posts,
    avg_views

from channel_stats