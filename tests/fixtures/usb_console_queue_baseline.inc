/* Extracted from the exact audited GPL-2.0 kernel sources; see preparer SHA pins. */
static void gs_complete_out(struct usb_ep *ep, struct usb_request *req)
{
	struct gscons_info *info = &gscons_info;

	switch (req->status) {
	default:
		pr_warn("%s: unexpected %s status %d\n",
			__func__, ep->name, req->status);
	case 0:
		/* normal completion */
		spin_lock(&info->con_lock);
		info->req_busy = 0;
		spin_unlock(&info->con_lock);

		wake_up_process(info->console_thread);
		break;
	case -ESHUTDOWN:
		/* disconnect */
		pr_vdebug("%s: %s shutdown\n", __func__, ep->name);
		break;
	}
}
static int gs_console_thread(void *data)
{
	struct gscons_info *info = &gscons_info;
	struct gs_port *port;
	struct usb_request *req;
	struct usb_ep *ep;
	int xfer, ret, count, size;

	do {
		port = info->port;
		set_current_state(TASK_INTERRUPTIBLE);
		if (!port || !port->port_usb
		    || !port->port_usb->in || !info->console_req)
			goto sched;

		req = info->console_req;
		ep = port->port_usb->in;

		spin_lock_irq(&info->con_lock);
		count = gs_buf_data_avail(&info->con_buf);
		size = ep->maxpacket;

		if (count > 0 && !info->req_busy) {
			set_current_state(TASK_RUNNING);
			if (count < size)
				size = count;

			xfer = gs_buf_get(&info->con_buf, req->buf, size);
			req->length = xfer;

			spin_unlock(&info->con_lock);
			ret = usb_ep_queue(ep, req, GFP_ATOMIC);
			spin_lock(&info->con_lock);
			if (ret < 0)
				info->req_busy = 0;
			else
				info->req_busy = 1;

			spin_unlock_irq(&info->con_lock);
		} else {
			spin_unlock_irq(&info->con_lock);
sched:
			if (kthread_should_stop()) {
				set_current_state(TASK_RUNNING);
				break;
			}
			schedule();
		}
	} while (1);

	return 0;
}
