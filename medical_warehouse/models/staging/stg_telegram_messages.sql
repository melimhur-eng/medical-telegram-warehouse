select

    cast(message_id as bigint) as message_id,

    trim(channel_name) as channel_name,

    cast(message_date as timestamp) as message_date,

    trim(message_text) as message_text,

    cast(views as integer) as views,

    cast(forwards as integer) as forwards,

    has_media,

    image_path,

    length(message_text) as message_length,

    case
        when image_path is null then false
        else true
    end as has_image

from {{ source('raw','telegram_messages') }}

where message_text is not null