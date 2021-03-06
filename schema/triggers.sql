create or replace function strip_all_triggers() returns text as $$ declare
    triggNameRecord record;
    triggTableRecord record;
begin
    for triggNameRecord in select distinct(trigger_name) from information_schema.triggers where trigger_schema = 'public' loop
        for triggTableRecord in select distinct(event_object_table) from information_schema.triggers where trigger_name = triggNameRecord.trigger_name loop
            raise notice 'Dropping trigger: % on table: %', triggNameRecord.trigger_name, triggTableRecord.event_object_table;
            execute 'drop trigger ' || triggNameRecord.trigger_name || ' on ' || triggTableRecord.event_object_table || ';';
        end loop;
    end loop;
    return 'done';
end;
$$ language plpgsql;

create or replace function notify_trigger() returns trigger as $$
declare
begin
    perform pg_notify('cache_invalidator', TG_TABLE_NAME);
    return null;
end;
$$ language plpgsql;

drop trigger if exists folders_trigger on folders;
create trigger folders_trigger after insert or update or delete on folders for each row execute procedure notify_trigger();

drop trigger if exists musics_trigger on musics;
create trigger musics_trigger after insert or update or delete on musics for each row execute procedure notify_trigger();

drop trigger if exists albums_trigger on albums;
create trigger albums_trigger after insert or update or delete on albums for each row execute procedure notify_trigger();

drop trigger if exists artists_trigger on artists;
create trigger artists_trigger after insert or update or delete on artists for each row execute procedure notify_trigger();

drop trigger if exists genres_trigger on genres;
create trigger genres_trigger after insert or update or delete on genres for each row execute procedure notify_trigger();

drop trigger if exists tags_trigger on tags;
create trigger tags_trigger after insert or update or delete on tags for each row execute procedure notify_trigger();

drop trigger if exists filters_trigger on filters;
create trigger filters_trigger after insert or update or delete on filters for each row execute procedure notify_trigger();

drop trigger if exists stats_trigger on stats;
create trigger stats_trigger after insert or update or delete on stats for each row execute procedure notify_trigger();

drop trigger if exists music_tags_trigger on music_tags;
create trigger music_tags_trigger after insert or update or delete on music_tags for each row execute procedure notify_trigger();
