import math


class Tracker:
    def __init__(self):
        # Store the center positions of the objects
        self.center_points = {}
        # Keep the count of the IDs
        # each time a new object id detected, the count will increase by one
        self.id_count = 0

    
    def get_iou(self,bb1, bb2):
            """
            Calculate the intersection over union (IoU) of two bounding boxes.
            """
            # Get the coordinates of bounding boxes
            b1_x1, b1_y1, b1_w, b1_h = bb1
            b1_x2, b1_y2 = b1_x1 + b1_w, b1_y1 + b1_h

            b2_x1, b2_y1, b2_w, b2_h = bb2
            b2_x2, b2_y2 = b2_x1 + b2_w, b2_y1 + b2_h

            # Calculate the coordinates of the intersection of the two bounding boxes
            x1 = max(b1_x1, b2_x1)
            y1 = max(b1_y1, b2_y1)
            x2 = min(b1_x2, b2_x2)
            y2 = min(b1_y2, b2_y2)

            # Calculate the area of the intersection
            intersection_area = max(0, x2 - x1) * max(0, y2 - y1)

            # Calculate the area of the two bounding boxes
            bb1_area = b1_w * b1_h
            bb2_area = b2_w * b2_h

            # Calculate the union area
            union_area = bb1_area + bb2_area - intersection_area

            # Calculate the IoU
            iou = intersection_area / union_area

            return iou
    
    def update(self, objects_rect):
        # Objects boxes and ids
        objects_bbs_ids = []
        
        # Get center point of new object
        for rect in objects_rect:
            x, y, w, h, c = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2

            # Find out if that object was detected already
            same_object_detected = False
            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])

                if dist < 50 :
                    self.center_points[id] = (cx, cy)
#                    print(self.center_points)
                    objects_bbs_ids.append([x, y, w, h, c, id])
                    same_object_detected = True
                    break

                # Calculate the IoU between the new bounding box and the existing bounding box
                bbox1 = (x, y, w, h)
                bbox2 = (pt[0]-w//2, pt[1]-h//2, w, h)
                iou = self.get_iou(bbox1, bbox2)

                # If the IoU is above a threshold, consider the new bounding box as the same object
                if iou > 0.5:
                    self.center_points[id] = (cx, cy)
                    objects_bbs_ids.append([x, y, w, h, c, id])
                    same_object_detected = True
                    break

            # New object is detected we assign the ID to that object
            if same_object_detected is False:
                self.center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x, y, w, h, c, self.id_count])
                self.id_count += 1

        # Clean the dictionary by center points to remove IDS not used anymore
        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, _, object_id= obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center

        # Update dictionary with IDs not used removed
        self.center_points = new_center_points.copy()
        return objects_bbs_ids
    
