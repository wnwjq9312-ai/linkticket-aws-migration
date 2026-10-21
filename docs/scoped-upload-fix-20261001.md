# WAS-1 upload and reward repair

- Only WAS-1 release `linkticket-20261001-postdeploy` was patched. No migrations or DDL ran.
- General uploads: MEDIA_ROOT and WEB_NFS_MOUNT `/nfs-storage`.
- NFT uploads: NFT_MEDIA_ROOT `/nfs/db_backup/nft_images`, NFT_NFS_MOUNT `/nfs/db_backup`, NFT_MEDIA_URL `/nft_images/`, NFT_UPLOADS_ENABLED=True.
- Existing performance genre CHECK stores Korean labels. A field adapter preserves API codes without changing existing rows.
- NFT management uses existing nft_item, including its unique token_id. Repeated form submissions reuse the record and do not write a second image.
- Event rewards use actual varchar reward_value; nonexistent reward_detail is not queried. Issuance locks the parent event before checking the event/member/type business key, preserving existing records without requiring a new constraint.
- Reward management records support/point entitlements only; external points, coupon generation and blockchain issuance are not implemented here.
- Member NFT lists, detail and image endpoints enforce ownership; staff can manage all. Favorites use member-scoped session state because the legacy favorite table targets another NFT model.
- Images use narrowly scoped Django FileResponse routes on WAS-1. No WEB/Proxy changes were made.

## Verification

Focused disposable tests: `python manage.py test events.test_scoped_uploads --settings=config.settings_schema_tests` — 3 passed. Never use that test settings module for deployment.

Candidate 18001 and operational WAS-1 8000 passed: poster DB/file/HTTP, NFT DB/file/HTTP, own mypage, other-member detail/image 404, other-member list isolation, repeated NFT/reward issuance. Original five NFT image hashes remained unchanged. No related seed/db_insert/SQL files were found; repeat checks cover issuance, not a nonexistent seed script.

New verification records were retained (no deletion): performance 2, nft_item 6, one ended verification event and one support reward for the existing test member.

## Backup / rollback

WAS-1 `/root/linkticket-scoped-upload-20261001-194607/` contains `code-before.tar.gz`, `production.env`, and `added-files.json`. To revert application behavior, restore backed-up code and env in their original locations, run Django check, then restart only gunicorn.service. New files can remain unused; do not remove NFS files or database records. Restoring the old env also restores its previously broken upload paths.

The environment file is `/etc/linkticket/releases/linkticket-20260930-211208.env`; it and the backup remain root-only and are not committed.

## Remaining scope boundaries

WAS-2 remains unchanged at user request; VIP requests routed there can retain old behavior. Migration history and other pre-existing model/migration discrepancies remain known issues. This patch adds no database migration and must not trigger automatic migrate.
