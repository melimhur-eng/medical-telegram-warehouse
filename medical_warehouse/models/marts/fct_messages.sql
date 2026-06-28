with base as (
    select *
    from {{ ref('stg_telegram_messages') }}
),

channels as (
    select *
    from {{ ref('dim_channels') }}
),

dates as (
    select *
    from {{ ref('dim_dates') }}
)

select

    {{ dbt_utils.generate_surrogate_key([
        'b.channel_name',
        'b.message_id'
    ]) }} as message_key,

    b.message_id,

    c.channel_key,

    d.date_key,

    b.message_text,

    b.message_length,

    b.views,

    b.forwards,

    b.has_image

from base b

left join channels c
    on b.channel_name = c.channel_name

left join dates d
    on b.message_date::date = d.full_date