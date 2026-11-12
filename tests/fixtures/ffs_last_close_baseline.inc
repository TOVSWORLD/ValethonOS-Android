/* Extracted from the exact audited GPL-2.0 kernel sources; see preparer SHA pins. */
static void ffs_data_closed(struct ffs_data *ffs)
{
	ENTER();

	if (atomic_dec_and_test(&ffs->opened)) {
		if (ffs->no_disconnect) {
			ffs->state = FFS_DEACTIVATED;
			if (ffs->epfiles) {
				ffs_epfiles_destroy(ffs->epfiles,
						   ffs->eps_count);
				ffs->epfiles = NULL;
			}
			if (ffs->setup_state == FFS_SETUP_PENDING)
				__ffs_ep0_stall(ffs);
		} else {
			ffs->state = FFS_CLOSING;
			ffs_data_reset(ffs);
		}
	}
	if (atomic_read(&ffs->opened) < 0) {
		ffs->state = FFS_CLOSING;
		ffs_data_reset(ffs);
	}

	ffs_data_put(ffs);
}
