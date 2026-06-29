with detections as (

    select *

    from {{ source('raw','image_detections') }}

),

messages as (

    select *

    from {{ ref('fct_messages') }}

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

    m.message_id,

    m.channel_key,

    m.date_key,

    d.detected_object,

    d.confidence_score,

    d.image_category

from messages m

join detections d

    on m.message_id = d.message_id