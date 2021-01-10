/*
 * $Id: spruce.h,v 1.5 2003/12/11 20:11:37 jastr Exp $
 *
 * This file is part of Spruce
 * Copyright (C) 2003 Jacob Strauss (jastr@lcs.mit.edu)
 * 
 * Spruce is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * Spruce is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with Spruce; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#ifndef __SPRUCE_H__
#define __SPRUCE_H__

#define SPRUCE_TCP_CONTROL_PORT 23877
#define SPRUCE_UDP_PORT  23876

#define min(a,b) ((a)>(b) ? (b) : (a))
#define max(a,b) ((a)>(b) ? (a) : (b))

/*control channel commands*/
#define CONTROL_NOOP 0x0
#define CONTROL_EXIT 0x4
#define CONTROL_ACK 0x40
#define CONTROL_SPRUCE_OUTPUT 0x2 //+ filename

#endif /*SPRUCE_H*/
